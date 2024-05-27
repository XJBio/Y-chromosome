import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
import pandas as pd
import os
import numpy as np

fontsize=40
linewidth=40

def plot_agp_assembly(agp_files, sample_list ,fai_file, output_path):
    # Load and parse FAI file
    fai_data = pd.read_csv(fai_file, sep='\t', header=None, names=['region', 'length', 'start_base','file_length','full_length'])
    regions_with_positions = []
    current_position = 0
    narrow_regions = []  # To collect names of narrow regions for the legend
    for index, row in fai_data.iterrows():
        start = current_position
        end = start + row['length']
        name = row['region'].replace("chrY_", "")
        if row['length'] > 2000000:  # Arbitrary threshold for 'long' regions
            pass
        else:
            narrow_regions.append(name)
        regions_with_positions.append((name, start, end, row['length']))
        current_position = end+1

    # Prepare the plot
    fig, ax = plt.subplots(figsize=(50, 7 + 2 * len(agp_files)))  # Dynamic height based on number of samples
    color_palette = plt.cm.tab20(np.linspace(0, 1, 20))  # Extended color palette for contigs
    plt.subplots_adjust(bottom=0.2)
 # Plot each region as a filled block
    narrow_legend_handles  = [] 
    for i, (name, start, end, length) in enumerate(regions_with_positions):
        color = color_palette[i % len(color_palette)]
        ax.fill_between([start, end], [0, 0], [0.3, 0.3], color=color, edgecolor='black', linewidth=1)
        if length > 2000000:
            ax.text(start + 0.1 * length, 0.02, name, ha='left', va='bottom', fontsize=fontsize, color='black', rotation=0)
        else:
            narrow_legend_handles.append(Line2D([0], [0], color=color, lw=4))
    ax.fill_between([end+1e6, end+1e7], [0, 0], [0.3, 0.3], color='white', edgecolor='white', linewidth=1)

    # Process each AGP file and plot the assembly paths
    sample_positions = {}
    contig_colors = {}  # Dictionary to store colors for contigs
    max_genomic_position = 0  # Track the maximum genomic position for labeling length
    for i, agp_file in enumerate(agp_files):
        sample_name = sample_list[i]  # Naming samples sequentially
        sample_positions[sample_name] = i + 1  # Assigning a unique Y-position for each sample

        agp_data = pd.read_csv(agp_file, sep='\t', header=None, names=['object', 'start', 'end', 'part_number', 'component_type', 'component_id', 'component_start', 'component_end', 'orientation'])
        agp_data = agp_data[agp_data['object']=='chrY_RagTag']
        sample_end_position = agp_data['end'].max()
        max_genomic_position = max(max_genomic_position, sample_end_position)
        for _, section in agp_data.iterrows():
            # Assign a unique color to each contig not seen before
            if section['component_id'] not in contig_colors:
                contig_colors[section['component_id']] = color_palette[len(contig_colors) % len(color_palette)]
            color = contig_colors[section['component_id']]
            ax.plot([section['start'], section['end']], [sample_positions[sample_name], sample_positions[sample_name]], color=color, linewidth=linewidth)
        # Label sample length at the end of its range
        ax.text(sample_end_position + 1e6, sample_positions[sample_name], f"{sample_end_position / 1e6:.2f} MB", ha='left', va='center', fontsize=fontsize, color='black')
    # plt.subplots_adjust(bottom=0.2)
    # Legend for narrow regions
    if narrow_regions:
        legend = ax.legend(narrow_legend_handles, narrow_regions, loc='upper center', bbox_to_anchor=(0.91, 0.95), title="Narrow Regions",title_fontsize=fontsize, fontsize=fontsize, ncol=1) 
        plt.gca().add_artist(legend)

    # Set plot titles and labels with adjusted font sizes
    ax.set_title("Visualization of chrY_RagTag Assembly for Multiple Samples", fontsize=fontsize+10)
    ax.set_xlabel("Genomic Position", fontsize=fontsize)
    ax.set_ylabel("Sample Names", fontsize=fontsize)
    ax.set_yticks([sample_positions[sample] for sample in sample_positions])
    ax.set_yticklabels([sample for sample in sample_positions], fontsize=fontsize)
    ax.tick_params(axis='x', labelsize=fontsize)  # Adjust x-tick label size if necessary
    ax.xaxis.get_offset_text().set_fontsize(fontsize)  # 调整偏移量标签的字体大小
    # Adjust layout and save the plot to the specified output path
    plt.tight_layout()  # Make space for the legend below the plot
    plt.savefig(output_path)

if __name__ == "__main__":
    data_dir  = '/data/home/sjwan/projects/Y-chromosome/workflow.output/data/verkko1.4'
    sample_list = os.listdir(data_dir)
    sample_list.sort()
    sample_list = sample_list[::-1]
    agp_files = []
    for sample in sample_list:
        agp_files.append(f'/data/home/sjwan/projects/Y-chromosome/workflow.output/03.assembly.workflow/{sample}/ragtag/ragtag.scaffold.agp')
    fai='/data/home/sjwan/projects/Y-chromosome/workflow.output/data/T2T_Y_subregion.fa.fai'
    out_image = '/data/home/sjwan/projects/Y-chromosome/workflow.output/03.assembly.workflow/img/agp.png'
    sample_list = [sample_name.split('_')[0] for sample_name in sample_list]
    plot_agp_assembly(agp_files, sample_list ,fai, out_image)