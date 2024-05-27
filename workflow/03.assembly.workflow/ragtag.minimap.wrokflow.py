import sys
import argparse
sys.path.append("/data/home/sjwan/projects/Y-chromosome/")
from utils.software import *
from utils.build_path import *


def load_workflow(workflow, sample):
    # 路径
    assembly = f'/data/home/sjwan/projects/Y-chromosome/workflow.output/data/verkko1.4/{sample}/assembly.fasta'
    reference = '/data/home/sjwan/projects/Y-chromosome/workflow.output/data/chm13v2.0.fa'

    OUTPUT_DIR = f'/data/home/sjwan/projects/Y-chromosome/workflow.output/03.assembly.workflow/{sample}'
    check_and_make_path(OUTPUT_DIR)
    RAGTAG_OUTPUT = join_and_make_path(OUTPUT_DIR, 'ragtag')

    ragtag = RagtagScaffoldDefaultMinimap(logger)
    ragtag.RUN_PARAMS['thread'] = '80'
    ragtag.RUN_PARAMS['reference'] = reference
    ragtag.RUN_PARAMS['query'] = assembly
    ragtag.RUN_PARAMS['output'] = RAGTAG_OUTPUT
    workflow.add_software(ragtag)

    

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Ragtag for a FA type.")
    parser.add_argument("log", type=str, help="Path to save the log file")
    
    args = parser.parse_args()
    data_dir  = '/data/home/sjwan/projects/Y-chromosome/workflow.output/data/verkko1.4'
    sample_list = os.listdir(data_dir)
    
    logger = setup_logger(args.log)
    logger.info(sample_list)
    ragtag_workflow = Workflow(logger)
    for sample in sample_list:
        load_workflow(ragtag_workflow, sample)
    ragtag_workflow.run('RUN')   
