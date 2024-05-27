import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import numpy as np
import matplotlib.patches as patches
import os


def parse_fai(fai_file):
    regions = []
    total_length = 0
    with open(fai_file, 'r') as f:
        for line in f:
            fields = line.strip().split('\t')
            region_name = fields[0]
            length = int(fields[1])
            start = total_length
            end = total_length + length
            total_length += length
            regions.append({
                'region_name': region_name,
                'start': start,
                'end': end,
                'length': length
            })
    return pd.DataFrame(regions)


def parse_paf(paf_file):
    data = []
    with open(paf_file, 'r') as f:
        for line in f:
            fields = line.strip().split('\t')
            query_name = fields[0]
            query_length = int(fields[1])
            query_start = int(fields[2])
            query_end = int(fields[3])
            strand = fields[4]
            target_name = fields[5]
            target_length = int(fields[6])
            target_start = int(fields[7])
            target_end = int(fields[8])
            residue_matches = int(fields[9])
            alignment_block_length = int(fields[10])
            mapping_quality = int(fields[11])
            tags = {tag.split(':')[0]: tag.split(':')[2] for tag in fields[12:]}

            data.append({
                'query_name': query_name,
                'query_length': query_length,
                'query_start': query_start,
                'query_end': query_end,
                'strand': strand,
                'target_name': target_name,
                'target_length': target_length,
                'target_start': target_start,
                'target_end': target_end,
                'residue_matches': residue_matches,
                'alignment_block_length': alignment_block_length,
                'mapping_quality': mapping_quality,
                **tags
            })

    return pd.DataFrame(data)


def parse_agp(agp_file):
    contigs = []
    with open(agp_file, 'r') as f:
        for line in f:
            if line.startswith('#') or line.startswith('##'):
                continue
            fields = line.strip().split('\t')
            object_name = fields[0]
            object_start = int(fields[1])
            object_end = int(fields[2])
            part_number = int(fields[3])
            component_type = fields[4]

            if component_type == 'W':
                component_id = fields[5]
                component_start = int(fields[6])
                component_end = int(fields[7])
                orientation = fields[8]

                contigs.append({
                    'object_name': object_name,
                    'object_start': object_start,
                    'object_end': object_end,
                    'part_number': part_number,
                    'component_type': component_type,
                    'component_id': component_id,
                    'component_start': component_start,
                    'component_end': component_end,
                    'orientation': orientation
                })
            elif component_type == 'U':
                contigs.append({
                    'object_name': object_name,
                    'object_start': object_start,
                    'object_end': object_end,
                    'part_number': part_number,
                    'component_type': component_type,
                    'component_id': fields[5],
                    'component_start': None,
                    'component_end': None,
                    'orientation': None
                })
    return pd.DataFrame(contigs)


def plot_alignment(fai_df, paf_df, agp_df, output_image):
    contig_region_width = 0.2
    coverage_region_width = 0.2
    fontsize = 16

    fig, ax = plt.subplots(figsize=(15, 5))

    # 预定义颜色映射
    colors = plt.colormaps.get_cmap('tab20')

    # 绘制参考序列的区域分布
    for idx, row in fai_df.iterrows():
        color = colors(idx / len(fai_df))
        ax.add_patch(patches.Rectangle((row['start'], 2.0 + coverage_region_width), row['length'], contig_region_width, edgecolor=color,
                                       facecolor=color, label=row['region_name'] if idx == 0 else ""))

    # 绘制参考序列的覆盖分布（灰色表示未覆盖区域）
    for idx, row in fai_df.iterrows():
        ax.add_patch(
            patches.Rectangle((row['start'], 2.0), row['length'], coverage_region_width, edgecolor='none', facecolor='grey', alpha=0.1))

    # 绘制组装的contigs分布
    for idx, row in agp_df.iterrows():
        if row['component_type'] == 'W':
            color = colors(idx % len(fai_df) / len(fai_df))  # 使用相同的颜色映射
            ax.add_patch(patches.Rectangle((row['object_start'], 1 - coverage_region_width - contig_region_width),
                                           row['object_end'] - row['object_start'], contig_region_width, edgecolor=color, facecolor=color,
                                           label=row['component_id'] if idx == 0 else ""))

    # 绘制组装的覆盖分布（灰色表示未覆盖区域）
    for idx, row in agp_df.iterrows():
        if row['component_type'] == 'W':
            ax.add_patch(patches.Rectangle((row['object_start'], 1 - coverage_region_width), row['object_end'] - row['object_start'],
                                           coverage_region_width, edgecolor='none', facecolor='grey', alpha=0.1))

    # 绘制比对区间之间的连线并填充颜色
    for idx, row in paf_df.iterrows():
        target_row = fai_df[fai_df['region_name'] == row['target_name']].iloc[0]
        target_start = target_row['start'] + row['target_start']
        target_end = target_row['start'] + row['target_end']
        query_start = row['query_start']
        query_end = row['query_end']

        if row['strand'] == '+':
            line_color = 'red'
        else:
            line_color = 'blue'

        # 绘制覆盖行中的比对区域
        ax.add_patch(
            patches.Rectangle((target_start, 2.0), target_end - target_start, coverage_region_width, edgecolor='none', facecolor=line_color,
                              alpha=0.5))
        ax.add_patch(
            patches.Rectangle((query_start, 1 - coverage_region_width), query_end - query_start, coverage_region_width, edgecolor='none',
                              facecolor=line_color, alpha=0.5))

        # 绘制连线并填充梯形区域
        verts = [(target_start, 2.0), (target_end, 2.0), (query_end, 1.0), (query_start, 1.0)]
        poly = patches.Polygon(verts, closed=True, edgecolor=line_color, facecolor=line_color, alpha=0.1)
        ax.add_patch(poly)

        # 突出显示连线
        ax.plot([target_start, query_start], [2.0, 1.00], color=line_color, lw=1, alpha=0.7)
        ax.plot([target_end, query_end], [2.0, 1.00], color=line_color, lw=1, alpha=0.7)

    ax.set_ylim(0, 3)
    ax.set_yticks([1 - coverage_region_width - contig_region_width / 2,
                   1 - coverage_region_width / 2,
                   2 + coverage_region_width / 2,
                   2 + coverage_region_width + contig_region_width / 2])
    ax.set_yticklabels(['Assembly', 'Assembly Coverage', 'Reference Coverage', 'Reference'], fontsize=fontsize)
    ax.set_xlabel('Genomic Position', fontsize=fontsize + 4)
    ax.set_title('Alignment of Assembly to Reference', fontsize=fontsize + 4)
    # ax.legend()
    plt.tight_layout()
    plt.savefig(output_image)
    plt.show()


def main(fa_name):
    fai_file = '/data/home/sjwan/projects/Y-chromosome/workflow.output/data/T2T_Y_subregion.fa.fai'
    paf_file = f'/data/home/sjwan/projects/Y-chromosome/workflow.output/03.assembly.workflow/{fa_name}/subregion.minimap/subregion.minimap.paf'
    agp_file = f'/data/home/sjwan/projects/Y-chromosome/workflow.output/03.assembly.workflow/{fa_name}/ragtag/ragtag.scaffold.agp'
    output_image = f'/data/home/sjwan/projects/Y-chromosome/workflow.output/03.assembly.workflow/img/{fa_name.split("_")[0]}.subregion.png'

    # 解析 FAI 文件
    fai_df = parse_fai(fai_file)

    # 解析 PAF 文件
    paf_df = parse_paf(paf_file)
    paf_df = paf_df[paf_df['mapping_quality'] >= 60]
    # 解析 AGP 文件
    agp_df = parse_agp(agp_file)
    agp_df = agp_df[agp_df['object_name'] == 'chrY_RagTag']
    # 绘制比对图
    plot_alignment(fai_df, paf_df, agp_df, output_image)


if __name__ == '__main__':
    data_dir = '/data/home/sjwan/projects/Y-chromosome/workflow.output/data/verkko1.4'
    sample_list = os.listdir(data_dir)
    sample_list.sort()
    sample_list = sample_list[::-1]
    depth_files = []

    for sample in sample_list:
        main(sample)
