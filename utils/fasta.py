import pysam
import os
from Bio import SeqIO

def read_fasta(file_path):
    sequences = {}
    fa = pysam.Fastafile(file_path)
    for key in fa.references:
        sequences[key] = fa.fetch(key)
    fa.close()
    return sequences

def search_Y(fa_data):
    for key in fa_data:
        if 'chrY' in key:
            return key, fa_data[key]
    return 'N', 'X'

def extract_Y(file_path, output_path):
    Y_name, hap1_Y = search_Y(read_fasta(file_path))
    with open(
        os.path.join(output_path), "w"
    ) as f:
        f.write(f">{Y_name}\n")
        f.write(hap1_Y + "\n")

def search_contig(fa_data, contig_name):
    for key in fa_data:
        if contig_name in key:
            return key, fa_data[key]
    return 'N', 'X'

def extract_contig(file_path, contig_name ,output_path):
    Y_name, hap1_Y = search_contig(read_fasta(file_path), contig_name)
    with open(
        os.path.join(output_path), "w"
    ) as f:
        f.write(f">{Y_name}\n")
        f.write(hap1_Y + "\n")

def extract_contigs(input_fasta, output_fasta, contig_ids):
    """
    从输入的FASTA文件中提取指定的contigs并写入新的FASTA文件

    :param input_fasta: 输入的FASTA文件路径
    :param output_fasta: 输出的FASTA文件路径
    :param contig_ids: 要提取的contig ID列表
    """
    # 读取输入的FASTA文件
    sequences = SeqIO.parse(input_fasta, "fasta")

    # 筛选出需要的contig
    selected_sequences = [seq for seq in sequences if seq.id in contig_ids]

    # 将选定的contig写入新的FASTA文件
    with open(output_fasta, "w") as output_handle:
        SeqIO.write(selected_sequences, output_handle, "fasta")
        

def split_fasta(input_fasta, output_dir):
    # 确保输出目录存在
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # 读取输入的fasta文件
    for seq_record in SeqIO.parse(input_fasta, "fasta"):
        # 构造输出文件名
        output_file = os.path.join(output_dir, f"{seq_record.id}.fasta")
        # 将每条序列写入单独的fasta文件
        with open(output_file, "w") as output_handle:
            SeqIO.write(seq_record, output_handle, "fasta")