from Bio import SeqIO
import os

def read_fasta(file):
    """ 读取FASTA文件并返回序列记录列表 """
    return list(SeqIO.parse(file, "fasta"))

input_fa = "/data/home/xfyang/CHN_Multi_Ethnic/RY01_Yao_Male_CNYAM0001/verkko_hifi_ont_hic/assembly.fasta"

output_dir="/data/home/sjwan/projects/Y-chromosome/pbs/out/RY01"

input_list = read_fasta(input_fa)

for record in input_list:
    if  'haplotype2-0000111' in record.id:
        ref_part = os.path.join(output_dir, f"{record.id}.fa")
        if not os.path.exists(ref_part):
            with open(ref_part, "w") as file:
                SeqIO.write(record, file, "fasta")
        break