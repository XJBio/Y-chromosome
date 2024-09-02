import sys
import argparse

sys.path.append("/data/home/sjwan/projects/Y-chromosome/")
from utils.software import *
from utils.build_path import *

def add_HMMER(workflow, sample, motif, out_dir):
    # 路径
    motif_path = f"/data/home/sjwan/projects/Y-chromosome/workflow.output/data/references_derived/{motif}.fasta"
    assembly_contigs = f"/data/home/sjwan/projects/Y-chromosome/workflow.output/data/verkko1.4/{sample}/assembly.fasta"

    motif_dir = join_and_make_path(out_dir, motif)

    out_txt = join_path(motif_dir, "motif.txt")
    out_table = join_path(motif_dir, "motif.tab")

    nhmmer = HMMER_nhmmer(logger)
    nhmmer.RUN_PARAMS["threads"] = "100"
    nhmmer.RUN_PARAMS["output_txt"] = out_txt
    nhmmer.RUN_PARAMS["output_table"] = out_table
    nhmmer.RUN_PARAMS["query_motif"] = motif_path
    nhmmer.RUN_PARAMS["assembly"] = assembly_contigs

    workflow.add_software(nhmmer)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="rules for identity XY.")
    parser.add_argument("log", type=str, help="Path to save the log file")
    parser.add_argument("mode", type=str, help="workflow mode")

    args = parser.parse_args()
    print(args)

    data_dir = "/data/home/sjwan/projects/Y-chromosome/workflow.output/data/verkko1.4"
    sample_list = os.listdir(data_dir)
    sample_list.sort()
    logger = setup_logger(args.log)
    
    motif_dir = '/data/home/sjwan/projects/Y-chromosome/workflow.output/data/references_derived'
    motif_list = os.listdir(motif_dir)
    motif_list.sort()
    motif_list = [motif.split('.')[0] for motif in motif_list]

    sample_flow = Workflow(logger)
    for sample in sample_list[1:]:
        output_dir = f"/data/home/sjwan/projects/Y-chromosome/workflow.output/03.assembly.workflow/{sample}"

        HMMER_OUTPUT = join_and_make_path(output_dir, "ALL.HMMER")
        for motif in motif_list:
            if 'HSat123_consensus_sequences' in motif or 'TSPY' in motif or 'HET3' in motif:
                continue
            add_HMMER(sample_flow, sample, motif, HMMER_OUTPUT)

    sample_flow.run(args.mode)
