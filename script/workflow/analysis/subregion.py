import pandas as pd
import numpy as np
import os
import sys
sys.path.append("/data/home/sjwan/projects/Y-chromosome")
from utils.load import *
from utils.fasta import *

sample_list = os.listdir(
    "/data/home/sjwan/projects/Y-chromosome/workflow.output/data/verkko1.4"
)
sample_list.sort()
subregion_fai = read_fai("/data/home/sjwan/projects/Y-chromosome/workflow.output/data/T2T_Y_subregion.fa.fai")
subregions_name = subregion_fai['contig'].to_list()
subregions_name = [name.replace('chrY_', '') for name in subregions_name]

quality_threshold = 1


paf_list = []
subregion_list = []
paf_colors = []
color_json = {}
for sample in sample_list:
    paf_path = f"/data/home/sjwan/projects/Y-chromosome/workflow.output/03.assembly.workflow/{sample}/minimap.subregion.Ycontigs/subregion.minimap.asm5.paf"
    subregion_paf = parse_paf(paf_path)
    subregion_paf = subregion_paf[subregion_paf["mapping_quality"] >= quality_threshold]
    subregion_list.append(subregion_paf)
    
def merge_intervals(intervals):
    # 按起始位置排序区间
    sorted_indices = np.argsort(intervals[:, 0])
    intervals = intervals[sorted_indices]

    merged = []
    for interval in intervals:
        # 如果合并后的列表是空的或者当前区间不与前一个合并后的区间重叠
        if not merged or merged[-1][1] < interval[0]:
            merged.append(interval)
        else:
            # 如果重叠，则合并区间
            merged[-1][1] = max(merged[-1][1], interval[1])

    return np.stack(merged)

def sum_region(merge_array):
    sum_length = 0
    for merge in merge_array:
        sum_length += merge[1] - merge[0]
    return sum_length

subregion_achieve = []
for paf in subregion_list:
    sub_list = paf['target_name'].unique()
    map_contigs = []
    for sub in sub_list:
        sub_paf = paf[paf['target_name'] == sub]
        sub_pos = merge_intervals(np.array(sub_paf[['target_start', 'target_end']]))
        map_p = sum_region(sub_pos)/np.max(sub_paf['target_length'])
        map_contigs.append([sub_paf['query_name'].unique(), sub, map_p])
    subregion_achieve.append(pd.DataFrame(map_contigs, columns=['contig', 'subregion', 'p']))
    
continue_counts = {}
for name in subregions_name:
    continue_counts[name] = 0

continue_df = np.zeros(shape=[len(sample_list),len(subregions_name)])

for sample_idx, map_contigs in enumerate(subregion_achieve):
    for region_idx, name in enumerate(subregions_name):
        continue_df[sample_idx, region_idx] = np.sum(map_contigs[map_contigs['subregion']=='chrY_'+name]['p'])
        if np.sum(map_contigs[map_contigs['subregion']=='chrY_'+name]['p']) > 0.95:
            continue_counts[name] += 1

continue_df = pd.DataFrame(continue_df, index=[sample.split('_')[0] for sample in sample_list], columns=subregions_name)

continue_df.to_csv("/data/home/sjwan/projects/Y-chromosome/workflow.output/03.assembly.workflow/analysis/subregion.csv")

import matplotlib.pyplot as plt

plt.figure(figsize=(10,6))
for name in continue_counts.keys():
    plt.bar(name, continue_counts[name])
plt.xticks(rotation=90)
plt.tight_layout()
plt.savefig('/data/home/sjwan/projects/Y-chromosome/workflow.output/03.assembly.workflow/analysis/subregion.continues.png')

