import sys
import argparse

sys.path.append("/data/home/sjwan/projects/Y-chromosome/")
from utils.software import *
from utils.build_path import *


def load_workflow(workflow, FA_NAME):
    # 路径
    assembly_contigs = f"/data/home/sjwan/projects/Y-chromosome/workflow.output/03.assembly.workflow/{FA_NAME}/ragtag/Y.contigs.fasta"

    OUTPUT_DIR = f"/data/home/sjwan/projects/Y-chromosome/workflow.output/03.assembly.workflow/{FA_NAME}"
    
    
    SOFT_OUTPUT = '/data/home/sjwan/tools/HumAS-HMMER_for_AnVIL/'
    # out_dir = join_and_make_path(SOFT_OUTPUT, monomers_name)
    
    os.system(f"cp {assembly_contigs} {SOFT_OUTPUT}/{FA_NAME}.Y.contigs.fa")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="RepeatMasker detect assembly gap.")
    parser.add_argument("log", type=str, help="Path to save the log file")
    parser.add_argument("mode", type=str, help="workflow mode")

    args = parser.parse_args()
    print(args)
    data_dir = "/data/home/sjwan/projects/Y-chromosome/workflow.output/data/verkko1.4"
    sample_list = os.listdir(data_dir)
    sample_list.sort()
    
    logger = setup_logger(args.log)
    sample_flow = Workflow(logger)
    
    for sample in sample_list:
        load_workflow(sample_flow, sample)    
    
    SOFT_OUTPUT = '/data/home/sjwan/tools/HumAS-HMMER_for_AnVIL/'
    humAS_HMMER = HumAS_HMMER(logger)
    humAS_HMMER.RUN_PARAMS["threads"] = "48"
    humAS_HMMER.RUN_PARAMS["fa_dir"] = SOFT_OUTPUT
    sample_flow.add_software(humAS_HMMER)
    sample_flow.run(args.mode)
