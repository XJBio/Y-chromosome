
"""
Step 1: 按质量分数过滤比对条目。
Step 2: 找出与 chrY 相关的比对条目。
Step 3: 过滤掉与任何非 chrY 参考序列比对总长度超过阈值的 contigs。
最终结果: 将符合条件的 chrY 比对条目与过滤后的结果合并，并保存到新的 PAF 文件中。
"""

import pandas as pd
import argparse

def read_paf(file_path):
    """Read PAF file into a DataFrame."""
    columns = [
        "query_name", "query_length", "query_start", "query_end",
        "target_name", "target_length", "target_start", "target_end",
        "match_bases", "alignment_length", "mapping_quality", "extra"
    ]
    return pd.read_csv(file_path, sep='\t', header=None, names=columns)

def filter_quality(df, min_quality):
    """Filter entries based on quality score."""
    return df[df['mapping_quality'] >= min_quality]

def filter_chrY_contigs(df):
    """Find contigs related to chrY."""
    return df[df['target_name'] == 'chrY']

def filter_contigs_by_total_alignment(df, overlap_threshold=1000000):
    """Filter contigs with total alignment length > 1MB on non-chrY references."""
    contig_groups = df.groupby('query_name')
    contigs_to_remove = []
    
    for contig, group in contig_groups:
        non_chrY_total = group[group['target_name'] != 'chrY']['alignment_length'].sum()
        if non_chrY_total > overlap_threshold:
            contigs_to_remove.append(contig)
    
    return df[~df['query_name'].isin(contigs_to_remove)]

def save_paf(df, output_file):
    """Save DataFrame to PAF file."""
    df.to_csv(output_file, sep='\t', header=False, index=False)

def main(input_paf, output_paf, min_quality, overlap_threshold):
    # Read the PAF file
    df = read_paf(input_paf)
    
    # Step 1: Filter based on quality score
    df = filter_quality(df, min_quality)
    
    # Step 2: Find contigs related to chrY
    chrY_contigs = filter_chrY_contigs(df)
    
    # Step 3: Filter contigs with total alignment length > 1MB on non-chrY references
    filtered_df = filter_contigs_by_total_alignment(df, overlap_threshold)
    
    # Ensure that we include chrY contigs that meet the criteria
    final_df = pd.concat([chrY_contigs, filtered_df])
    final_df = final_df.drop_duplicates()
    
    # Save the filtered PAF file
    save_paf(final_df, output_paf)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Filter PAF file for chrY related alignments.")
    parser.add_argument("input_paf", type=str, help="Path to the input PAF file")
    parser.add_argument("output_paf", type=str, help="Path to save the filtered PAF file")
    parser.add_argument("--min_quality", type=int, default=30, help="Minimum quality score to filter alignments (default: 30)")
    parser.add_argument("--overlap_threshold", type=int, default=1000000, help="Overlap threshold for total alignment length on non-chrY references in base pairs (default: 1000000)")
    
    args = parser.parse_args()
    
    main(args.input_paf, args.output_paf, args.min_quality, args.overlap_threshold)
