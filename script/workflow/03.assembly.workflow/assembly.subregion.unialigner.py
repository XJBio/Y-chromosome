import pandas as pd
import argparse
import os
import sys

sys.path.append("/data/home/sjwan/projects/Y-chromosome/")

from utils.software import *
from utils.build_path import *
from utils.load import *
from utils.fasta import *


def load_workflow(workflow, sample):
    outdir = f'/data/home/sjwan/projects/Y-chromosome/workflow.output/03.assembly.workflow/{sample}/unialigner/'
    assembly = f'/data/home/sjwan/projects/Y-chromosome/workflow.output/data/verkko1.4/{sample}/contigs.max10.Y.fasta'
    T2T_Y = '/data/home/sjwan/projects/Y-chromosome/workflow.output/data/T2TY.fa'
    tmp_dir = f'/data/home/sjwan/projects/Y-chromosome/workflow.output/03.assembly.workflow/{sample}/tmp/'
    check_and_make_path(outdir)
    check_and_make_path(tmp_dir)
    
    # split_fasta(assembly, tmp_dir)
    
    contigs = os.listdir(tmp_dir)
    
    for contig in contigs:
        minimap = UniAligner(logger)
        minimap.RUN_PARAMS['first'] = T2T_Y
        minimap.RUN_PARAMS['second'] = join_path(tmp_dir, contig)
        minimap.RUN_PARAMS['output_dir'] = join_and_make_path(outdir, contig.split('.')[0])
        workflow.add_software(minimap)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Unialigner for a FA type.")
    parser.add_argument("log", type=str, help="Path to save the log file")

    args = parser.parse_args()
    data_dir = '/data/home/sjwan/projects/Y-chromosome/workflow.output/data/verkko1.4'
    sample_list = os.listdir(data_dir)
    sample_list.sort()
    logger = setup_logger(args.log)

    veritymap_flow = Workflow(logger)
    for sample in sample_list:
        load_workflow(veritymap_flow, sample)
    veritymap_flow.run('RUN')
