import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.cm as cm


def plot_ref_paf(paf_df, save_path):
    # 假设paf_df是你的PAF数据
    # column_names和读取PAF文件的代码省略

    # 使用映射质量作为颜色映射的基础
    # 首先获取映射质量的最小值和最大值，以便正规化
    # min_quality = paf_df['mapping_quality'].min()
    # max_quality = paf_df['mapping_quality'].max()

    # 创建颜色映射对象
    # norm = plt.Normalize(min_quality, max_quality)
    cmap = cm.get_cmap('viridis')  # 你可以选择不同的colormap

    # 创建图形和坐标轴
    fig, ax = plt.subplots(figsize=(16, 16))
    color_mapping = {name: plt.cm.get_cmap('viridis')(i / len(paf_df['target_name'].unique())) for i, name in enumerate(paf_df['target_name'].unique())}

    # 对于PAF文件中的每一行，绘制一条从(query_start, target_start)到(query_end, target_end)的线

        
        # 绘制线
    for target_name, group in paf_df.groupby('target_name'):
        ax.plot([group['query_start'], group['query_end']], [group['target_start'], group['target_end']], 
                 color=color_mapping[target_name], label=target_name, alpha=0.7)

    # 添加颜色条
    # sm = cm.ScalarMappable(cmap=cmap, norm=norm)
    # sm.set_array([])
    # cbar = plt.colorbar(sm, ax=ax)
    # cbar.set_label('Mapping Quality')
    # 设置标签
# 解决图例重复的问题
    handles, labels = plt.gca().get_legend_handles_labels()
    by_label = dict(zip(labels, handles))  # 创建标签到句柄的映射，去除重复
    plt.legend(by_label.values(), by_label.keys(), title='Target Name')

    plt.grid(True)
    ax.set_aspect('equal')
    ax.set_xlabel('Query Position')
    ax.set_ylabel('Target Position')
    ax.set_title('Genome Alignment Visualization')
    plt.savefig(save_path, bbox_inches='tight')