import sys
import argparse

sys.path.append("/data/home/sjwan/projects/Y-chromosome/")
from utils.software import *
from utils.build_path import *


def load_workflow(workflow, FA_NAME):
    # 路径
    motif_path = "/data/home/sjwan/projects/Y-chromosome/workflow.output/data/references_derived/DYZ2_Yq.fasta"
    motif_name = "DYZ2_Yq"
    assembly_contigs = f"/data/home/sjwan/projects/Y-chromosome/workflow.output/03.assembly.workflow/{FA_NAME}/ragtag/Y.contigs.fasta"

    OUTPUT_DIR = f"/data/home/sjwan/projects/Y-chromosome/workflow.output/03.assembly.workflow/{FA_NAME}"
    HMMER_OUTPUT = join_and_make_path(OUTPUT_DIR, "hmmer")
    out_dir = join_and_make_path(HMMER_OUTPUT, motif_name)

    out_txt = join_path(out_dir, "motif.txt")
    out_table = join_path(out_dir, "motif.tab")

    nhmmer = HMMER_nhmmer(logger)
    nhmmer.RUN_PARAMS["threads"] = "48"
    nhmmer.RUN_PARAMS["output_txt"] = out_txt
    nhmmer.RUN_PARAMS["output_table"] = out_table
    nhmmer.RUN_PARAMS["query_motif"] = motif_path
    nhmmer.RUN_PARAMS["assembly"] = assembly_contigs

    workflow.add_software(nhmmer)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="nhmmer detect assembly gap.")
    parser.add_argument("log", type=str, help="Path to save the log file")
    parser.add_argument("mode", type=str, help="workflow mode")

    args = parser.parse_args()
    print(args)

    data_dir = "/data/home/sjwan/projects/Y-chromosome/workflow.output/data/verkko1.4"
    sample_list = os.listdir(data_dir)
    logger = setup_logger(args.log)

    sample_flow = Workflow(logger)
    for sample in sample_list:
        load_workflow(sample_flow, sample)
    sample_flow.run(args.mode)
