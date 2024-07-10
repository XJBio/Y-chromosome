import sys
import argparse
sys.path.append("/data/home/sjwan/projects/Y-chromosome/")
from utils.software import *
from utils.build_path import *
import gzip
import shutil

def read_fofn(fofn_path):
    """
    读取fofn文件，返回文件路径列表
    """
    with open(fofn_path, 'r') as f:
        files = f.read().strip().split('\n')
    return files

def merge_fastq_files_with_system_tools(output_fastq, input_fastq_files):
    with open(output_fastq, 'wb') as f_out:
        for fastq_file in input_fastq_files:
            subprocess.run(['zcat', fastq_file], stdout=f_out)
        subprocess.run(['gzip', output_fastq])


def load_workflow(workflow, sample):
    # 路径
    fq = f'/data/home/sjwan/projects/Y-chromosome/workflow.output/data/verkko1.4/{sample}/reads.minimap.Y.fq'
    # assembly = f'/data/home/sjwan/projects/Y-chromosome/workflow.output/03.assembly.workflow/{sample}/ragtag/Y.contigs.fasta'
    assembly = f'/data/home/sjwan/projects/Y-chromosome/workflow.output/data/verkko1.4/{sample}/assembly.fasta'
    TEMP_OUTPUT = f'/data/home/sjwan/projects/Y-chromosome/workflow.output/03.assembly.workflow/{sample}/'
    VERITYMAP_OUTPUT = f'/data/home/sjwan/projects/Y-chromosome/workflow.output/03.assembly.workflow/{sample}/veritymap'
    check_and_make_path(VERITYMAP_OUTPUT)
    # merge_fastq_files_with_system_tools(tmp_fq, fq_list)
    
    
    veritymap = VerityMap(logger)
    veritymap.RUN_PARAMS['thread'] = '48'
    veritymap.RUN_PARAMS['output'] = VERITYMAP_OUTPUT
    veritymap.RUN_PARAMS['reads'] = fq
    veritymap.RUN_PARAMS['assembly'] = assembly
    logger.info(veritymap.RUN_PARAMS)
    workflow.add_software(veritymap)

    

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="VeritypMap for a FA type.")
    parser.add_argument("log", type=str, help="Path to save the log file")
    
    args = parser.parse_args()
    data_dir  = '/data/home/sjwan/projects/Y-chromosome/workflow.output/data/verkko1.4'
    sample_list = os.listdir(data_dir)
    sample_list.sort()
    logger = setup_logger(args.log)
    
    veritymap_flow = Workflow(logger)
    for sample in sample_list:
        load_workflow(veritymap_flow, sample)
    veritymap_flow.run('RUN')   
