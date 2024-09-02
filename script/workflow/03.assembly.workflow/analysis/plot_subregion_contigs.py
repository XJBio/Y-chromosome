import matplotlib.pyplot as plt
import matplotlib.patches as patches
import matplotlib.colors as mcolors
import pandas as pd
import numpy as np
from matplotlib.gridspec import GridSpec
import os
import sys
from merge_contigs_map import merge_contigs_with_alignment
import json

sys.path.append("/data/home/sjwan/projects/Y-chromosome/")
from utils.software import *
from utils.build_path import *
from utils.load import *
from utils.plot_func.plot_paf import parse_fai

# 创建颜色


def generate_n_colors_tab20(n):
    colors = plt.cm.tab20(np.linspace(0, 1, n))
    hex_colors = [mcolors.to_hex(color) for color in colors]
    return hex_colors

# 自定义 JSON 编码器
class NumpyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        return json.JSONEncoder.default(self, obj)

# 示例数据创建
fai_data = [
    ["chrY_PAR1", 2458320, "#97CB99"],
    ["chrY_XDR1", 268516, "#FFEF57"],
    ["chrY_XTR1", 3187958, "#EEA9BA"],
    ["chrY_AMPL1", 285816, "#88C0EA"],
    ["chrY_XTR2", 199999, "#EEA9BA"],
    ["chrY_XDR2", 837831, "#FFEF57"],
    ["chrY_AMPL2", 3211045, "#88C0EA"],
    ["chrY_other1", 66831, "#D9D8DB"],
    ["chrY_HET1_centro1", 5822, "#777777"],
    ["chrY_HET1_centroDYZ3", 366184, "#7E2341"],
    ["chrY_HET1_centro2", 1767921, "#777777"],
    ["chrY_XDR3", 2234838, "#FFEF57"],
    ["chrY_AMPL3", 73851, "#88C0EA"],
    ["chrY_XDR4", 1816372, "#FFEF57"],
    ["chrY_AMPL4", 30092, "#88C0EA"],
    ["chrY_XDR5", 254679, "#FFEF57"],
    ["chrY_AMPL5", 266261, "#88C0EA"],
    ["chrY_XDR6", 1029967, "#FFEF57"],
    ["chrY_AMPL6", 1414352, "#88C0EA"],
    ["chrY_XDR7", 1184698, "#FFEF57"],
    ["chrY_HET2_DYZ19", 264878, "#777777"],
    ["chrY_XDR8", 984754, "#FFEF57"],
    ["chrY_AMPL7", 5251674, "#88C0EA"],
    ["chrY_other2_DYZ18", 155124, "#D9D8DB"],
    ["chrY_HET3_Yq", 34505764, "#777777"],
    ["chrY_PAR2", 336457, "#97CB99"],
]

columns = ["Region", "Length", "Color"]
fai = pd.DataFrame(fai_data, columns=columns)

# 计算起止坐标
fai["Start"] = fai["Length"].cumsum().shift(fill_value=0)
fai["End"] = fai["Start"] + fai["Length"]

# 去除'chrY_'前缀
fai["Region"] = fai["Region"].str.replace("chrY_", "")

# 设置多个区域的起始位置和放缩因子
regions = [
    {"start": 0, "end": 2458320, "scale": 5, "ticks": 2},
    {"start": 2458320, "end": 2726836, "scale": 1, "ticks": 2},
    {"start": 2726836, "end": 5914794, "scale": 1, "ticks": 2},
    {"start": 5914794, "end": 6200610, "scale": 1, "ticks": 2},
    {"start": 6200610, "end": 6400609, "scale": 1, "ticks": 2},
    {"start": 6400609, "end": 7238440, "scale": 1, "ticks": 2},
    {"start": 7238440, "end": 10449485, "scale": 1, "ticks": 2},
    {"start": 10449485, "end": 10516316, "scale": 1, "ticks": 2},
    {"start": 10516316, "end": 10522138, "scale": 1, "ticks": 2},
    {"start": 10522138, "end": 10888322, "scale": 1, "ticks": 2},
    {"start": 10888322, "end": 12656243, "scale": 5, "ticks": 2},
    {"start": 12656243, "end": 14891081, "scale": 1, "ticks": 2},
    {"start": 14891081, "end": 14964932, "scale": 1, "ticks": 2},
    {"start": 14964932, "end": 16781304, "scale": 1, "ticks": 2},
    {"start": 16781304, "end": 16811396, "scale": 1, "ticks": 2},
    {"start": 16811396, "end": 17066075, "scale": 1, "ticks": 2},
    {"start": 17066075, "end": 17332336, "scale": 1, "ticks": 2},
    {"start": 17332336, "end": 18362303, "scale": 1, "ticks": 2},
    {"start": 18362303, "end": 19776655, "scale": 1, "ticks": 2},
    {"start": 19776655, "end": 20961353, "scale": 1, "ticks": 2},
    {"start": 20961353, "end": 21226231, "scale": 1, "ticks": 2},
    {"start": 21226231, "end": 22210985, "scale": 1, "ticks": 2},
    {"start": 22210985, "end": 27462659, "scale": 1, "ticks": 2},
    {"start": 27462659, "end": 27617783, "scale": 1, "ticks": 2},
    {"start": 27617783, "end": 62123547, "scale": 5, "ticks": 2},
    {"start": 62123547, "end": 62460004 + 1e6, "scale": 2, "ticks": 2},
]

region_size = 0.45
region_height = 0.3
# 设定质量阈值
quality_threshold = 30

sample_list = os.listdir(
    "/data/home/sjwan/projects/Y-chromosome/workflow.output/data/verkko1.4"
)
sample_list.sort()


paf_list = []
paf_colors = []
color_json = {}
for sample in sample_list:
    paf_path = f"/data/home/sjwan/projects/Y-chromosome/workflow.output/03.assembly.workflow/{sample}/minimap.subregion.Ycontigs/T2T.minimap.paf"
    temp_paf = parse_paf(paf_path)
    # temp_paf = merge_contigs_with_alignment(temp_paf)
    temp_paf =  temp_paf[temp_paf["mapping_quality"] >= quality_threshold]
    paf_list.append(temp_paf)
    color_names = temp_paf[~temp_paf["query_name"].str.contains("unassigned")][
        "query_name"
    ].unique()
    temp_colors = generate_n_colors_tab20(len(color_names))
    color_dict = {}
    for name, color in zip(color_names, temp_colors):
        color_dict[name] = color
    paf_colors.append(color_dict)
    color_json[sample] = color_dict

# 将颜色写入 JSON 文件
json_file = '/data/home/sjwan/projects/Y-chromosome/workflow.output/03.assembly.workflow/analysis/color.json'
with open(json_file, 'w') as json_file:
    json.dump(color_json, json_file, indent=4, cls=NumpyEncoder)
    
    
# 样本数量
n_samples = len(paf_list) + 1
# 创建图表和GridSpec
fig = plt.figure(figsize=(18, n_samples * 1))
gs = GridSpec(1, len(regions), width_ratios=[r["scale"] for r in regions], wspace=0.01)

# 绘制每个区域
axes = []
for i, region in enumerate(regions):
    ax = fig.add_subplot(gs[i])
    axes.append(ax)
    for sample_idx in range(n_samples):
        y_offset = sample_idx * region_size  # 为每个样本设置不同的Y轴位置
        if sample_idx == 0:
            for j, row in fai.iterrows():
                if row["Start"] < region["end"] and row["End"] > region["start"]:
                    # 绘制矩形
                    ax.add_patch(
                        patches.Rectangle(
                            (max(row["Start"], region["start"]), y_offset),  # (x,y)
                            min(row["End"], region["end"])
                            - max(row["Start"], region["start"]),  # width
                            height=region_height,  # height
                            edgecolor="black",
                            facecolor=row["Color"],
                            alpha=0.8,
                        )
                    )
                    # 绘制文字标签
                    if row["Start"] >= region["start"] and row["End"] <= region["end"]:
                        text_x = row["Start"] + row["Length"] / 2
                    elif row["Start"] < region["start"]:
                        text_x = (
                            region["start"]
                            + (min(row["End"], region["end"]) - region["start"]) / 2
                        )
                    else:
                        text_x = row["Start"] + (region["end"] - row["Start"]) / 2
                    # 四个位置轮换
                    if j % 4 == 0:
                        text_y = y_offset + 0.2 * region_height
                    elif j % 4 == 1:
                        text_y = y_offset + 0.4 * region_height
                    elif j % 4 == 2:
                        text_y = y_offset + 0.6 * region_height
                    else:
                        text_y = y_offset + 0.8 * region_height
                    ax.text(
                        text_x,
                        text_y,
                        row["Region"],
                        ha="center",
                        va="center",
                        fontsize=8,
                        color="black",
                    )

        else:
            df = paf_list[sample_idx - 1]
            color_dict = paf_colors[sample_idx - 1]
            for j, row in df.iterrows():
                if "unassigned" in row["query_name"]:
                    color = "black"
                    continue
                else:
                    color = color_dict[row["query_name"]]
                if (
                    row["target_start"] < region["end"]
                    and row["target_end"] > region["start"]
                ):
                    # 绘制矩形
                    ax.add_patch(
                        patches.Rectangle(
                            (
                                max(row["target_start"], region["start"]),
                                y_offset,
                            ),  # (x,y)
                            min(row["target_end"], region["end"])
                            - max(row["target_start"], region["start"]),  # width
                            height=region_height,  # height
                            edgecolor="black",
                            facecolor=color,
                            alpha=0.8,
                        )
                    )

    # 设置X轴范围和刻度
    ax.set_xlim(region["start"], region["end"])
    tick_interval = (region["end"] - region["start"]) / region["ticks"]
    if i == 0:
        ticks = np.arange(region["start"], region["end"] + tick_interval, tick_interval)
    else:
        ticks = np.arange(
            region["start"] + tick_interval,
            region["end"] + tick_interval,
            tick_interval,
        )
    ax.set_xticks(ticks)
    ax.set_xticklabels([f"{x / 1000000:.2f}MB" for x in ticks], rotation=90)

# 统一设置所有子区域的Y轴属性
for ax in axes:
    ax.set_ylim(-region_height * 0.2, n_samples * region_size + region_height * 0.2)
    ax.set_yticks([region_height / 2 + i * region_size for i in range(n_samples)])
    ax.set_yticklabels(["T2TY"] + sample_list)
    ax.set_ylabel("Samples")

# 设置整体标题
fig.suptitle("DNA Sequence Regions", fontsize=16)

# 隐藏除第一个子图外的所有Y轴刻度
for ax in axes[1:]:
    ax.yaxis.set_visible(False)

# 添加断轴标记以在子图之间显示中断
# for i in range(len(axes) - 1):
#     d = .015  # 断轴标记的大小
#     kwargs = dict(transform=axes[i].transAxes, color='k', clip_on=False)
#     axes[i].plot((1 - d, 1 + d), (-d, +d), **kwargs)  # 右上角
#     axes[i].plot((1 - d, 1 + d), (1 - d, 1 + d), **kwargs)  # 右下角
#
#     kwargs.update(transform=axes[i + 1].transAxes)  # 切换到下一个子图的坐标系
#     axes[i + 1].plot((-d, +d), (1 - d, 1 + d), **kwargs)  # 左下角
#     axes[i + 1].plot((-d, +d), (-d, +d), **kwargs)  # 左上角

# 调整布局以适应所有元素
plt.subplots_adjust(top=0.9, bottom=0.15, wspace=0)

# plt.tight_layout()
# plt.savefig('/data/home/sjwan/projects/Y-chromosome/workflow.output/03.assembly.workflow/analysis/contig_subregion.png')
# plt.savefig(
#     "/data/home/sjwan/projects/Y-chromosome/workflow.output/03.assembly.workflow/analysis/contig_subregion_merge_part2.png"
# )
# plt.savefig(
#     # "/data/home/sjwan/projects/Y-chromosome/workflow.output/03.assembly.workflow/analysis/contig_subregion_part1.png"
# )
# plt.savefig(
#     "/data/home/sjwan/projects/Y-chromosome/workflow.output/03.assembly.workflow/analysis/contig_subregion_no_unassigned.png"
# )

# plt.savefig(
#     "/data/home/sjwan/projects/Y-chromosome/workflow.output/03.assembly.workflow/analysis/merge_subregion_no_unassigned.png"
# )

plt.savefig(
    "/data/home/sjwan/projects/Y-chromosome/workflow.output/03.assembly.workflow/analysis/contig_filter.png"
)
