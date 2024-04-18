from Bio import SeqIO
import os
import multiprocessing
import itertools
import subprocess

def read_fasta(file):
    """ 读取FASTA文件并返回序列记录列表 """
    return list(SeqIO.parse(file, "fasta"))

def run_unialigner(exc_path, chrom1, chrom2, output):
    cmd = f"{exc_path} --first {chrom1} --second {chrom2} -o {output}"
    print(cmd)
    # subprocess.run(cmd, shell=True)

class UniAligner:
    
    def __init__(self, exc_path, max_thread=1):
        self.exc_path = exc_path
        self.max_thread =max_thread
    
    def run(self, target_fa, ref_fa, output_dir):
        """读取fasta文件序列列表"""
        target_fa_list = read_fasta(target_fa)
        ref_fa_list = read_fasta(ref_fa)
        
        """将参考序列的各个序列分开，保存到输出文件夹的tmp文件夹中"""
        for record in ref_fa_list:
            ref_part = os.path.join(output_dir,'tmp', f"{record.id}.fa")
            if not os.path.exists(ref_part):
                with open(ref_part, "w") as file:
                    SeqIO.write(record, file, "fasta")
                    
        """多线程并行执行比对任务"""
        task_list = [(self.exc_path,record1, record2, os.path.join(output_dir,f"{record1.id}",f"{record2.id}"))  
                     for record1, record2 in itertools.product(target_fa_list, ref_fa_list)] 
        pool = multiprocessing.Pool(processes=self.max_thread)
        results = pool.map(run_unialigner, task_list)
        
        print('stdout:', results.stdout)
        print('stderr:', results.stderr)
        
        
        
        
                    
        
        
        