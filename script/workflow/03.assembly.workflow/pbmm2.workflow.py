import sys
import argparse
sys.path.append("/data/home/sjwan/projects/Y-chromosome/")
from utils.software import *
from utils.build_path import *


def load_workflow(workflow, FA_NAME):
    # 路径
    fofn = f'/data/home/sjwan/projects/Y-chromosome/workflow.output/data/verkko1.4/{FA_NAME}/assembly.fofn'
    assembly = f'/data/home/sjwan/projects/Y-chromosome/workflow.output/data/verkko1.4/{FA_NAME}/assembly.fasta'
    mni = f'/data/home/sjwan/projects/Y-chromosome/workflow.output/data/verkko1.4/{FA_NAME}/assembly.fasta.mmi'
    outbam = f'/data/home/sjwan/projects/Y-chromosome/workflow.output/data/verkko1.4/{FA_NAME}/assembly.fasta.pbmm.bam'
    filterbam = f'/data/home/sjwan/projects/Y-chromosome/workflow.output/data/verkko1.4/{FA_NAME}/assembly.fasta.pbmm.2308.bam'
    sortbam = f'/data/home/sjwan/projects/Y-chromosome/workflow.output/data/verkko1.4/{FA_NAME}/assembly.fasta.pbmm.sort.bam'
    with open(fofn, 'r') as f:
        reads_list = f.readlines()

    OUTPUT_DIR = f'/data/home/sjwan/projects/Y-chromosome/workflow.output/03.assembly.workflow/{FA_NAME}'
    PBMM_OUTPUT = join_path(OUTPUT_DIR, 'pbmm2')
    NUCFLAG_OUTPUT = join_path(OUTPUT_DIR, 'nucflag')
    

    pbmm2_index = Pbmm2_index(logger)
    pbmm2_index.RUN_PARAMS['contig'] = assembly
    pbmm2_index.RUN_PARAMS['mmi'] = mni
    
    
    pbmm2_align = Pbmm2_align(logger)
    pbmm2_align.RUN_PARAMS['thread'] = '48'
    pbmm2_align.RUN_PARAMS['mmi'] = mni
    pbmm2_align.RUN_PARAMS['fofn'] = fofn
    pbmm2_align.RUN_PARAMS['outbam'] = outbam
    
    samtools_view_2308 = Samtools_view_2308(logger)
    samtools_view_2308.RUN_PARAMS['thread'] = '48'
    samtools_view_2308.RUN_PARAMS['inputbam'] = outbam
    samtools_view_2308.RUN_PARAMS['outbam'] = filterbam
    
    samtools_sort = Samtools_sort_bam(logger)
    samtools_sort.RUN_PARAMS['thread'] = '48'
    samtools_sort.RUN_PARAMS['inputbam'] = filterbam
    samtools_sort.RUN_PARAMS['outbam'] = sortbam
    
    samtools_index = Samtools_index_bam(logger)
    samtools_index.RUN_PARAMS['thread'] = '48'
    samtools_index.RUN_PARAMS['inputbam'] = sortbam
    
    
    workflow.add_software(pbmm2_index)
    workflow.add_software(pbmm2_align)
    workflow.add_software(samtools_view_2308)
    workflow.add_software(samtools_sort)
    workflow.add_software(samtools_index)
    
    

    

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="NucFlag for a FA type.")
    parser.add_argument("log", type=str, help="Path to save the log file")
    
    args = parser.parse_args()
    data_dir  = '/data/home/sjwan/projects/Y-chromosome/workflow.output/data/verkko1.4'
    sample_list = os.listdir(data_dir)
    logger = setup_logger(args.log)
    
    veritymap_flow = Workflow(logger)
    for sample in sample_list:
        load_workflow(veritymap_flow, sample)
    veritymap_flow.run('RUN')   
