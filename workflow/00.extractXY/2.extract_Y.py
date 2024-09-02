import pandas as pd
import sys

sys.path.append("/data/home/sjwan/projects/Y-chromosome/")
from utils.software import *
from utils.build_path import *
from utils.load import parse_paf


def parse_paf(paf_file):
    data = []
    with open(paf_file, "r") as f:
        for line in f:
            fields = line.strip().split("\t")
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

            # 过滤比对质量小于30的结果
            if mapping_quality >= 30:
                tags = {}
                for tag in fields[12:]:
                    try:
                        key, type_, value = tag.split(":")
                        tags[key] = value
                    except ValueError:
                        continue

                data.append(
                    {
                        "query_name": query_name,
                        "query_length": query_length,
                        "query_start": query_start,
                        "query_end": query_end,
                        "strand": strand,
                        "target_name": target_name,
                        "target_length": target_length,
                        "target_start": target_start,
                        "target_end": target_end,
                        "residue_matches": residue_matches,
                        "alignment_block_length": alignment_block_length,
                        "mapping_quality": mapping_quality,
                        **tags,
                    }
                )

    return pd.DataFrame(data)


def parse_paf_files(y_paf_file, x_paf_file):
    """
    解析Y染色体和X染色体的PAF文件，返回DataFrame。
    """
    y_paf = parse_paf(y_paf_file)
    # x_paf = parse_paf(x_paf_file)
    return y_paf, None


def merge_intervals(intervals):
    """
    合并重叠的区间
    """
    sorted_intervals = sorted(intervals, key=lambda x: x[0])
    merged_intervals = []

    for interval in sorted_intervals:
        if not merged_intervals or merged_intervals[-1][1] < interval[0]:
            merged_intervals.append(interval)
        else:
            merged_intervals[-1][1] = max(merged_intervals[-1][1], interval[1])

    return merged_intervals


def calculate_coverage_length(intervals):
    """
    计算覆盖长度
    """
    merged_intervals = merge_intervals(intervals)
    coverage_length = sum(end - start for start, end in merged_intervals)
    return coverage_length


def filter_primary_y_contigs(y_paf, x_paf):
    """
    筛选主要比对到Y染色体且不比对到X染色体，并且Y染色体比对部分超过90%的contig。
    返回包含每个contig的名称、长度以及比对到Y染色体的百分比的DataFrame。
    """
    # 获取比对到X染色体的query_name
    # x_contigs = set(x_paf["query_name"].unique())

    # 筛选比对到Y染色体且不比对到X染色体的contig
    y_paf_filtered = y_paf.copy()

    # 计算每个contig比对到Y染色体的覆盖长度
    y_paf_filtered.loc[:, "intervals"] = y_paf_filtered.apply(
        lambda row: [row["query_start"], row["query_end"]], axis=1
    )
    y_intervals = (
        y_paf_filtered.groupby("query_name")["intervals"].apply(list).reset_index()
    )
    y_intervals["y_coverage_length"] = y_intervals["intervals"].apply(
        calculate_coverage_length
    )

    # 合并查询长度信息
    query_lengths = (
        y_paf_filtered.groupby("query_name")["query_length"].max().reset_index()
    )

    # 合并覆盖长度和查询长度
    merged_contigs = pd.merge(y_intervals, query_lengths, on="query_name")

    # 计算比对到Y染色体的百分比
    merged_contigs["y_alignment_percentage"] = (
        merged_contigs["y_coverage_length"] / merged_contigs["query_length"]
    )

    # 筛选比对到Y染色体部分超过90%的contig
    primary_y_contigs = merged_contigs[merged_contigs["y_alignment_percentage"] > 0.7]

    return primary_y_contigs[["query_name", "query_length", "y_alignment_percentage"]]


def rule_1_main(y_paf_file, x_paf_file):
    """
    主程序：实现Rule 1，提取主要比对到Y染色体且不比对到X染色体，并且Y染色体比对部分超过90%的contig。
    输出包含每个contig的名称、长度以及比对到Y染色体的百分比的DataFrame。
    """
    # 解析Y染色体和X染色体的PAF文件
    y_paf, x_paf = parse_paf_files(y_paf_file, x_paf_file)

    # 筛选主要比对到Y染色体且不比对到X染色体，并且Y染色体比对部分超过90%的contig
    primary_y_contigs_df = filter_primary_y_contigs(y_paf, x_paf)

    return primary_y_contigs_df


data_dir = "/data/home/sjwan/projects/Y-chromosome/workflow.output/data/verkko1.4"
sample_list = os.listdir(data_dir)
sample_list.sort()
# sample = sample_list[4]
for sample in sample_list:
    print(sample)
    # 示例使用
    y_paf_file = f"/data/home/sjwan/projects/Y-chromosome/workflow.output/03.assembly.workflow/{sample}/ALL.minimap2XY/minimap2.Y.paf"
    x_paf_file = f"/data/home/sjwan/projects/Y-chromosome/workflow.output/03.assembly.workflow/{sample}/ALL.minimap2XY/minimap2.X.paf"

    primary_y_contigs_df = rule_1_main(y_paf_file, x_paf_file)
    print(primary_y_contigs_df.sort_values(by=["query_length"], ascending=False).head(10))
