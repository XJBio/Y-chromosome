from Bio import SeqIO
import subprocess
import itertools
import os

def read_fasta(file):
    """ 读取FASTA文件并返回序列记录列表 """
    return list(SeqIO.parse(file, "fasta"))

def run_comparison(chrom1, chrom2, output):
    """ 对两个chromosome运行外部比较命令 """
    cmd = f"/home/sjwan/tools/unialigner/tandem_aligner/build/bin/tandem_aligner --first {chrom1} --second {chrom2} -o {output}"
    subprocess.run(cmd, shell=True)

def compare_chromosomes(fasta1, fasta2, tmp_dir):
    """ 从两个FASTA文件中提取chromosome并进行两两比较 """
    seqs1 = read_fasta(fasta1)
    seqs2 = read_fasta(fasta2)

    # 生成两两组合
    for record1, record2 in itertools.product(seqs1, seqs2):
        # print(f"{record1.id}.{record2.id}")
        chrom1 = os.path.join(tmp_dir, f"{record1.id}.fa")
        chrom2 = os.path.join(tmp_dir, f"{record2.id}.fa")
        
        # 将每个记录写入临时文件
        with open(chrom1, "w") as file1:
            SeqIO.write(record1, file1, "fasta")
        if not os.path.exists(chrom2):
            with open(chrom2, "w") as file2:
                SeqIO.write(record2, file2, "fasta")
        # 运行外部命令比较这两个文件
        run_comparison(chrom1, chrom2, os.path.join(tmp_dir,f"{record1.id}.{record2.id}"))

# 用你的实际文件名替换这里的'config1.fa'和'config2.fa'

config1 = '/home/sjwan/ESA/hifiasm/ESA.samples/JPZ0325/JPZ0325.hap1.fa'
ref = '/home/sjwan/ESA/reference/chm13v2.0.Y.sub.fa'
temp_dir = '/home/sjwan/ESA/workflow/6_test_unialigner/output/JPZ30225/temp'
compare_chromosomes(config1, ref, temp_dir)
