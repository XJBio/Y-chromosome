import sys
import argparse
sys.path.append("/data/home/sjwan/projects/Y-chromosome/")
from utils.software import *
from utils.build_path import *

def load_workflow(workflow, FA_NAME):
    # 路径
    hifi_path = f'/data/DATA/Human_genomes/reference_based_analysis/aligned_reads/CHN_Multi_Ethnic/RY_align/{FA_NAME}/hifi'
    bam = join_path(hifi_path, f'CHN_Multi_Ethnic.{FA_NAME}.GRCh38.HiFi.minimap2.sorted.bam')
    Y_bam = f'/data/home/sjwan/projects/Y-chromosome/workflow.output/data/verkko1.4/{FA_NAME}/GRCh38.minimap2.sorted.Y.bam'
    depth = f'/data/home/sjwan/projects/Y-chromosome/workflow.output/data/verkko1.4/{FA_NAME}/GRCh38.minimap2.sorted.Y.depth'

    
    samtoos_view_chromesome = Samtools_view_name(logger)
    samtoos_view_chromesome.RUN_PARAMS['inputbam'] = bam
    samtoos_view_chromesome.RUN_PARAMS['outbam'] = Y_bam
    samtoos_view_chromesome.RUN_PARAMS['name'] = 'chrY'
    samtoos_view_chromesome.RUN_PARAMS['thread'] = '48'
    
    samtoos_depth_chromesome = Samtools_depth(logger)
    samtoos_depth_chromesome.RUN_PARAMS['inputbam'] = Y_bam
    samtoos_depth_chromesome.RUN_PARAMS['depth'] = depth
    
    workflow.add_software(samtoos_view_chromesome)
    workflow.add_software(samtoos_depth_chromesome)
    
    
    

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="depth for a FA type.")
    parser.add_argument("log", type=str, help="Path to save the log file")
    
    args = parser.parse_args()
    data_dir  = '/data/home/sjwan/projects/Y-chromosome/workflow.output/data/verkko1.4'
    sample_list = os.listdir(data_dir)
    logger = setup_logger(args.log)
    
    veritymap_flow = Workflow(logger)
    for sample in sample_list:
        load_workflow(veritymap_flow, sample)
    veritymap_flow.run('RUN')   