import sys
import argparse
sys.path.append("/data/home/sjwan/projects/Y-chromosome/")
from utils.software import *
from utils.build_path import *


def load_workflow(workflow, sample):
    # 路径
    fofn = f'/data/home/xfyang/CHN_Multi_Ethnic/{sample}/hifi_raw_fq/'
    assembly = f'/data/home/sjwan/projects/Y-chromosome/workflow.output/data/verkko1.4/{sample}/assembly.fasta'
    # assembly2 = f'/data/home/sjwan/projects/Y-chromosome/workflow.output/data/verkko1.4/{sample}/assembly.haplotype2.fasta'
    fq_list = os.listdir(fofn)

    OUTPUT_DIR = f'/data/home/sjwan/projects/Y-chromosome/workflow.output/03.assembly.workflow/{sample}'
    check_and_make_path(OUTPUT_DIR)
    VERITYMAP_OUTPUT = join_and_make_path(OUTPUT_DIR, 'veritymap')

    for read in fq_list:
        if '.fastq.gz' in read:
            veritymap = VerityMap(logger)
            veritymap.RUN_PARAMS['thread'] = '48'
            veritymap.RUN_PARAMS['output'] = VERITYMAP_OUTPUT
            veritymap.RUN_PARAMS['reads'] = join_path(fofn, read.rstrip())
            veritymap.RUN_PARAMS['assembly'] = assembly
            logger.info(veritymap.RUN_PARAMS)
            workflow.add_software(veritymap)

    

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="VeritypMap for a FA type.")
    parser.add_argument("log", type=str, help="Path to save the log file")
    
    args = parser.parse_args()
    data_dir  = '/data/home/sjwan/projects/Y-chromosome/workflow.output/data/verkko1.4'
    sample_list = os.listdir(data_dir)
    logger = setup_logger(args.log)
    
    veritymap_flow = Workflow(logger)
    for sample in sample_list:
        load_workflow(veritymap_flow, sample)
    veritymap_flow.run('RUN')   
