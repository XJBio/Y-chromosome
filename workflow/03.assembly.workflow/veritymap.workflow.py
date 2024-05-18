import sys
import argparse
sys.path.append("/data/home/sjwan/projects/Y-chromosome/")
from utils.software import *
from utils.build_path import *


def load_workflow(workflow, sample):
    # 路径
    fofn = f'/data/home/sjwan/projects/Y-chromosome/workflow.output/data/verkko1.4/{sample}/assembly.fofn'
    assembly1 = f'/data/home/sjwan/projects/Y-chromosome/workflow.output/data/verkko1.4/{sample}/assembly.haplotype1.fasta'
    assembly2 = f'/data/home/sjwan/projects/Y-chromosome/workflow.output/data/verkko1.4/{sample}/assembly.haplotype2.fasta'
    with open(fofn, 'r') as f:
        reads_list = f.readlines()

    OUTPUT_DIR = f'/data/home/sjwan/projects/Y-chromosome/workflow.output/03.assembly.workflow/{sample}'
    VERITYMAP_OUTPUT = join_path(OUTPUT_DIR, 'veritymap')

    for read in reads_list:
        veritymap = VerityMap(logger)
        veritymap.RUN_PARAMS['thread'] = '48'
        veritymap.RUN_PARAMS['output'] = VERITYMAP_OUTPUT
        veritymap.RUN_PARAMS['reads'] = read.rstrip()
        veritymap.RUN_PARAMS['assembly1'] = assembly1
        veritymap.RUN_PARAMS['assembly2'] = assembly2
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
