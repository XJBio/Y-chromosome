import sys
import argparse
sys.path.append("/data/home/sjwan/projects/Y-chromosome/")
from utils.software import *
from utils.build_path import *
from utils.fasta import extract_Y

def load_workflow(workflow, sample):
    # 路径
    # assembly = f'/data/home/sjwan/projects/Y-chromosome/workflow.output/03.assembly.workflow/{sample}/ragtag/ragtag.scaffold.fasta'
    # assembly_Y = f'/data/home/sjwan/projects/Y-chromosome/workflow.output/03.assembly.workflow/{sample}/ragtag/ragtag.scaffold.Y.fasta'
    Y_contigs = f'/data/home/sjwan/projects/Y-chromosome/workflow.output/03.assembly.workflow/{sample}/ragtag/Y.contigs.fasta'
    subregion_T2T_Y = '/data/home/sjwan/projects/Y-chromosome/workflow.output/data/T2T_Y_subregion.fa'
    # assembly2 = f'/data/home/sjwan/projects/Y-chromosome/workflow.output/data/verkko1.4/{sample}/assembly.haplotype2.fasta'

    # extract_Y(assembly, assembly_Y)

    OUTPUT_DIR = f'/data/home/sjwan/projects/Y-chromosome/workflow.output/03.assembly.workflow/{sample}/minimap.subregion.Ycontigs'
    # os.system(f'rm -rf {OUTPUT_DIR}')
    check_and_make_path(OUTPUT_DIR)
    PAF_OUTPUT = join_path(OUTPUT_DIR, 'subregion.minimap.asm5.paf')
    minimap_ragtag2reference = Minimap2_asm5(logger)
    minimap_ragtag2reference.RUN_PARAMS['target'] = subregion_T2T_Y
    minimap_ragtag2reference.RUN_PARAMS['query'] = Y_contigs
    minimap_ragtag2reference.RUN_PARAMS['output'] = PAF_OUTPUT
    minimap_ragtag2reference.RUN_PARAMS['thread'] = '48'
    workflow.add_software(minimap_ragtag2reference)
    

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="subregion for a FA type.")
    parser.add_argument("log", type=str, help="Path to save the log file")
    
    args = parser.parse_args()
    data_dir  = '/data/home/sjwan/projects/Y-chromosome/workflow.output/data/verkko1.4'
    sample_list = os.listdir(data_dir)
    logger = setup_logger(args.log)
    
    subregion_workflow = Workflow(logger)
    for sample in sample_list:
        load_workflow(subregion_workflow, sample)
    subregion_workflow.run('RUN')   