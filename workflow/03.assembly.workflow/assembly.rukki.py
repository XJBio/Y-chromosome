import sys
import argparse
sys.path.append("/data/home/sjwan/projects/Y-chromosome/")
from utils.software import *
from utils.build_path import *


def load_workflow(workflow, FA_NAME):
    # 路径
    assembly_graph = f'/data/home/xfyang/CHN_Multi_Ethnic/{FA_NAME}/verkko_hifi_ont_hic/assembly.homopolymer-compressed.noseq.gfa'
    XY_contig_table = f'/data/home/xfyang/CHN_Multi_Ethnic/{FA_NAME}/verkko_hifi_ont_hic/assembly.paths.tsv'

    OUTPUT_DIR = f'/data/home/sjwan/projects/Y-chromosome/workflow.output/03.assembly.workflow/{FA_NAME}'
    RUKKI_OUTPUT = join_and_make_path(OUTPUT_DIR, 'rukki')
    
    out_path = join_path(RUKKI_OUTPUT, 'path.tsv')
    node_assign_path = join_path(RUKKI_OUTPUT, 'node_assign.tsv')
    
    

    rukki_detect = Rukki(logger)
    rukki_detect.RUN_PARAMS['assembly_graph'] = assembly_graph
    rukki_detect.RUN_PARAMS['XY_contig_table'] = XY_contig_table
    rukki_detect.RUN_PARAMS['out_paths'] = out_path
    rukki_detect.RUN_PARAMS['out_node_assignment'] = node_assign_path
    
    workflow.add_software(rukki_detect)
    
    

    

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Rukki detect assembly gap.")
    parser.add_argument("log", type=str, help="Path to save the log file")
    parser.add_argument("mode", type=str, help="workflow mode")
    
    args = parser.parse_args()
    print(args)
    
    data_dir  = '/data/home/sjwan/projects/Y-chromosome/workflow.output/data/verkko1.4'
    sample_list = os.listdir(data_dir)
    logger = setup_logger(args.log)
    
    sample_flow = Workflow(logger)
    for sample in sample_list:
        load_workflow(sample_flow, sample)
    sample_flow.run(args.mode)   
