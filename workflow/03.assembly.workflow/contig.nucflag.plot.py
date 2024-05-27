import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import numpy as np
import matplotlib.patches as patches
import os
import sys
import argparse

sys.path.append("/data/home/sjwan/projects/Y-chromosome/")
from utils.software import *
from utils.build_path import *
from utils.load import *

BASE_DIR = '/data/home/sjwan/projects/Y-chromosome/workflow.output'

plot_legend = {
    'COLLAPSE_VAR': 0,  # 蓝色
    'COLLAPSE': 0,  # 橙色
    'GAP': 0,  # 绿色
    'MISJOIN': 0
}


def plot_nucflag_var(ax, agp_df, misasm, i):
    contig_region_width = 1
    colors = plt.colormaps.get_cmap('tab10')
    unique_names = agp_df['component_id'].unique()
    colors = [colors(i / len(unique_names)) for i in range(len(unique_names))]
    color_map = dict(zip(unique_names, colors))
    for idx, row in agp_df.iterrows():
        color = color_map[row['component_id']]
        # color = '#22f'
        if row['component_type'] == 'W':
            ax.add_patch(patches.Rectangle((row['object_start'], i * 3 + 2), row['object_end'] - row['object_start'], contig_region_width,
                                           edgecolor=color, facecolor=color))

    ax.add_patch(patches.Rectangle((min(agp_df['object_start']), i * 3 + 1.5), max(agp_df['object_end']) - min(agp_df['object_start']), 0.5,
                                   edgecolor=color, facecolor='#bcbcbc', alpha=0.75))

    color_map = {
        'COLLAPSE_VAR': '#fb7252',  # 蓝色
        'COLLAPSE': '#a15eff',  # 橙色
        'GAP': '#353535',  # 绿色
        'MISJOIN': '#0074ff'  # 红色
    }

    for idx, row in misasm.iterrows():
        color = color_map[row['type']]
        if row['name'] == 'Unkown':
            ax.add_patch(patches.Rectangle((row['start'], i * 3 + 1.5), row['end'] - row['start'], 0.5,
                                           edgecolor=color, facecolor=color, label=row['type'] if plot_legend[row['type']] == 0 else '',
                                           alpha=0.75))
        else:
            contig_start = agp_df[agp_df['component_id'] == row['name']]['object_start'].iloc[0]
            ax.add_patch(patches.Rectangle((contig_start + row['start'], i * 3 + 1.5), row['end'] - row['start'], 0.5,
                                           edgecolor=color, facecolor=color, label=row['type'] if plot_legend[row['type']] == 0 else '',
                                           alpha=0.75))
        plot_legend[row['type']] = 1


def main(ax, fa_name, i):
    fai_file = f'{BASE_DIR}/data/T2T_Y_subregion.fa.fai'
    paf_file = f'{BASE_DIR}/03.assembly.workflow/{fa_name}/subregion.minimap/subregion.minimap.paf'
    agp_file = f'{BASE_DIR}/03.assembly.workflow/{fa_name}/ragtag/ragtag.scaffold.agp'
    output_image = f'{BASE_DIR}/03.assembly.workflow/img/{fa_name.split("_")[0]}.subregion.png'

    # 解析 PAF 文件
    paf_df = parse_paf(paf_file)
    # paf_df = paf_df[paf_df['mapping_quality']>=60]
    # 解析 AGP 文件
    agp_df = parse_agp(agp_file)
    agp_df = agp_df[agp_df['object_name'] == 'chrY_RagTag']

    misasm_list = []

    for idx, row in agp_df.iterrows():
        if row['component_type'] == 'W':
            misasm = f'{BASE_DIR}/03.assembly.workflow/{fa_name}/nucflag/{row["component_id"]}.misasm.bed'
            if os.path.exists(misasm):
                try:
                    misasm_list.extend(load_misasm_bed(misasm))
                except pd.errors.EmptyDataError:
                    continue
        if row['component_type'] == 'U':
            misasm_list.append(['Unkown', row['object_start'], row['object_end'], 'GAP'])
    misasm_df = pd.DataFrame(misasm_list, columns=['name', 'start', 'end', 'type'])
    # 绘制比对图

    plot_nucflag_var(ax, agp_df, misasm_df, i)


if __name__ == '__main__':
    data_dir = '/data/home/sjwan/projects/Y-chromosome/workflow.output/data/verkko1.4'
    sample_list = os.listdir(data_dir)
    sample_list.sort()
    sample_list = sample_list[::-1]
    depth_files = []

    fig, ax = plt.subplots(figsize=(20, 8))
    ax.set_yticks([3 * i + 2.5 for i in range(len(sample_list))])
    ax.set_yticklabels([sample.split('_')[0] for sample in sample_list], fontsize=20)
    ax.tick_params(axis='x', labelsize=15)
    plt.ylim(1, 3 * len(sample_list) + 1)
    plt.xlim(-100, 60000000)
    for idx, sample in enumerate(sample_list):
        main(ax, sample, idx)
    plt.xlabel("Position", fontsize=20)
    plt.ylabel("Sample", fontsize=20)
    plt.title("Visualization of NucFlag Annotations", fontsize=20)
    plt.legend(fontsize=15)
    plt.tight_layout()
    plt.savefig("/data/home/sjwan/projects/Y-chromosome/workflow.output/03.assembly.workflow/img/nucflag.png")
