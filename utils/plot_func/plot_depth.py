import matplotlib.pyplot as plt
import matplotlib.cm as cm
import os
from tqdm import tqdm
import numpy as np

def plot_multiple_coverages(depth_files, labels, output_image):
    plt.figure(figsize=(15, 5))
    
    # 自动生成颜色列表
    color_map = plt.get_cmap('viridis', len(depth_files))
    colors = [color_map(i) for i in range(len(depth_files))]

    for i, depth_file in tqdm(enumerate(depth_files)):
        positions = []
        coverages = []
        
        with open(depth_file, 'r') as depth:
            for line in depth:
                chrom, pos, cov = line.strip().split('\t')
                positions.append(int(pos))
                coverages.append(int(cov))
        positions = np.array(positions)
        coverages = np.array(coverages)
        all_positions = np.arange(0, np.max(positions)+1)
        all_coverages = np.zeros_like(all_positions)
        all_coverages[positions] = coverages
        # np.save()
        # coverages[coverages == 0] = 1
        mean_coverage = np.mean(all_coverages)
        plt.plot(all_positions, all_coverages, label=labels[i] + f' Coverage: {mean_coverage:.2f}', color=colors[i], alpha=0.5)

    plt.xlabel('Position on Y chromosome', fontsize=22)
    plt.ylabel('Coverage (log scale)', fontsize=22)
    plt.title('Coverage Distribution on Y Chromosome', fontsize=22)
    plt.yscale('log')  # 设置纵坐标为对数刻度
    plt.legend(fontsize=22)
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(os.path.join(output_image,"depth.png"))
    plt.close()

# 示例使用
# depth_files = ['chrY_sample1.depth', 'chrY_sample2.depth', 'chrY_sample3.depth']
# labels = ['Sample 1', 'Sample 2', 'Sample 3']
# output_image = 'multiple_coverage_distribution.png'
# plot_multiple_coverages(depth_files, labels, output_image)


if __name__ == "__main__":
    data_dir  = '/data/home/sjwan/projects/Y-chromosome/workflow.output/data/verkko1.4'
    sample_list = os.listdir(data_dir)
    sample_list.sort()
    sample_list = sample_list[::-1]
    depth_files = []
    for sample in sample_list:
        depth_files.append(f'/data/home/sjwan/projects/Y-chromosome/workflow.output/data/verkko1.4/{sample}/GRCh38.minimap2.sorted.Y.depth')
    fai='/data/home/sjwan/projects/Y-chromosome/workflow.output/data/T2T_Y_subregion.fa.fai'
    out_image = '/data/home/sjwan/projects/Y-chromosome/workflow.output/03.assembly.workflow/img/'
    sample_list = [sample_name.split('_')[0] for sample_name in sample_list]
    print(sample_list)
    print(depth_files)
    plot_multiple_coverages(depth_files, sample_list, out_image)
