import sys
import argparse

sys.path.append("/data/home/sjwan/projects/Y-chromosome/")
from utils.software import *
from utils.build_path import *


def load_workflow(workflow, FA_NAME, name, path):
    # 路径
    monomers_path = path
    monomers_name = name
    assembly_contigs = f"/data/home/sjwan/projects/Y-chromosome/workflow.output/03.assembly.workflow/{FA_NAME}/ragtag/Y.contigs.fasta"

    OUTPUT_DIR = f"/data/home/sjwan/projects/Y-chromosome/workflow.output/03.assembly.workflow/{FA_NAME}"
    SOFT_OUTPUT = join_and_make_path(OUTPUT_DIR, "stringdecomposer")
    out_dir = join_and_make_path(SOFT_OUTPUT, monomers_name)


    stringdecomposer = StringDecomposer(logger)
    stringdecomposer.RUN_PARAMS["threads"] = "48"
    stringdecomposer.RUN_PARAMS["out_dir"] = out_dir
    stringdecomposer.RUN_PARAMS["sequences"] = assembly_contigs
    stringdecomposer.RUN_PARAMS["monomers"] = monomers_path

    workflow.add_software(stringdecomposer)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="nhmmer detect assembly gap.")
    parser.add_argument("log", type=str, help="Path to save the log file")
    parser.add_argument("mode", type=str, help="workflow mode")

    args = parser.parse_args()
    print(args)
    data_dir = "/data/home/sjwan/projects/Y-chromosome/workflow.output/data/verkko1.4"
    sample_list = os.listdir(data_dir)
    sample_list.sort()
    
    logger = setup_logger(args.log)
    sample_flow = Workflow(logger)
    
    
    monomer_dir = '/data/home/sjwan/projects/Y-chromosome/workflow.output/data/references_derived/'
    monomers_list = ['HSat123_consensus_sequences.fa']
    
    for monomer in monomers_list:
        for sample in sample_list:
            load_workflow(sample_flow, sample, monomer.split('_')[0], join_path(monomer_dir,monomer))
    sample_flow.run(args.mode)
