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
    agp_file = f'/data/home/sjwan/projects/Y-chromosome/workflow.output/03.assembly.workflow/{sample}/ragtag/ragtag.scaffold.agp'
    assembly_file = f'/data/home/sjwan/projects/Y-chromosome/workflow.output/data/verkko1.4/{sample}/assembly.fasta'
    extract_Y_contigs_assembly = f'/data/home/sjwan/projects/Y-chromosome/workflow.output/data/verkko1.4/{sample}/contigs.ragtag.Y.fasta'
    T2T_Y = '/data/home/sjwan/projects/Y-chromosome/workflow.output/data/T2TY.fa'
    output_paf = f'/data/home/sjwan/projects/Y-chromosome/workflow.output/03.assembly.workflow/{sample}/T2TY.minimap/ragtag.Y.paf'
    agp = parse_agp(agp_file)
    agp_contigs = agp[agp['component_type'] == 'W']

    exclude_chr_apg = agp_contigs[~agp_contigs['object_name'].str.contains('chr', case=False, na=False)]
    include_chr_agp = agp_contigs[agp_contigs['object_name'].str.contains('chr', case=False, na=False)]

    exclude_chr_contigs = exclude_chr_apg['component_id'].tolist()

    chr_contigs_name = include_chr_agp['object_name'].unique().tolist()

    chr_contigs = {}
    Y_contigs = []
    for name in chr_contigs_name:
        if 'chrY' in name:
            Y_contigs = include_chr_agp[include_chr_agp['object_name'].str.contains(name, case=False, na=False)]['component_id'].tolist()
            continue
        chr_contigs[name] = include_chr_agp[include_chr_agp['object_name'].str.contains(name, case=False, na=False)][
            'component_id'].tolist()

    not_overlap_contigs = []

    for contig in Y_contigs:
        for key in chr_contigs.keys():
            if contig in chr_contigs[key]:
                print(contig)
                continue
        not_overlap_contigs.append(contig)
    not_overlap_contigs.extend(exclude_chr_contigs)

    # 接下来从assembly fasta中抽取对应的contigs

    extract_contigs(assembly_file, extract_Y_contigs_assembly, not_overlap_contigs)

    # 使用minimap 对提取后的contigs 进行映射 然后绘制覆盖图

    minimap = Minimap2_asm20(logger)
    minimap.RUN_PARAMS['target'] = T2T_Y
    minimap.RUN_PARAMS['query'] = extract_Y_contigs_assembly
    minimap.RUN_PARAMS['thread'] = '48'
    minimap.RUN_PARAMS['output'] = output_paf
    workflow.add_software(minimap)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="NucFlag for a FA type.")
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
