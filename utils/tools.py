from Bio import SeqIO
import os
import multiprocessing
import itertools
import subprocess
from utils.build_path import check_and_make_path, join_path
import re


def read_fasta(file):
    """ 读取FASTA文件并返回序列记录列表 """
    return list(SeqIO.parse(file, "fasta"))


def run_unialigner(exc_path, chrom1, chrom2, output):
    cmd = f"{exc_path} --first {chrom1} --second {chrom2} -o {output}"
    print(cmd)
    # subprocess.run(cmd, shell=True)


def sliding_split_sequence(long_seq, window_size, step_size):
    chunks = []
    for start in range(0, len(long_seq) - window_size + 1, step_size):
        end = start + window_size
        chunks.append([long_seq[start:end], start, end])
    if end < len(long_seq):
        # 如果最后一个块不完整，从前一个完整块扩展
        remaining = len(long_seq) - end
        start = len(long_seq) - window_size
        chunks.append([long_seq[start:end], start, len(long_seq)])
    return chunks


def parse_cigar(cigar):
    pattern = re.compile(r'(\d+)([MIDNSHPX=])')
    return [(int(length), op) for length, op in pattern.findall(cigar)]


def cigar_to_paf(query_name, query_length, query_start, target_name, target_length, target_start, cigar):
    parsed_cigar = parse_cigar(cigar)
    query_end = query_start
    target_end = target_start
    match_length = 0
    total_length = 0

    for length, op in parsed_cigar:
        if op == 'M' or op == '=':
            query_end += length
            target_end += length
            match_length += length
            total_length += length
        elif op == 'I':
            query_end += length
            total_length += length
        elif op == 'D':
            target_end += length
            total_length += length

    paf_record = [
        query_name, str(query_length), str(query_start), str(query_end),
        '+', target_name, str(target_length), str(target_start), str(target_end),
        str(match_length), str(total_length), '60', cigar
    ]
    return '\t'.join(paf_record)


def save_chunks(chunks, save_path):
    # 将每个分块保存到单独的fasta文件
    chunk_path = []
    for i, slide in enumerate(chunks):
        chunk, start, end = slide
        filename = join_path(save_path, f"{chunk.id}_{start}_{end}.fa")
        SeqIO.write(chunk, filename, "fasta")
        print(f"Saved {filename}")
        chunk_path.append(filename)
    return chunk_path


def save_chunk(slide, save_path):
    chunk, start, end = slide
    filename = join_path(save_path, f"{chunk.id}_{start}_{end}.fa")
    SeqIO.write(chunk, filename, "fasta")
    print(f"Saved {filename}")
    return filename


class UniAligner:

    def __init__(self, exc_path, max_thread=1):
        self.exc_path = exc_path
        self.max_thread = max_thread

    def run(self, target_fa, ref_fa, output_dir):
        """读取fasta文件序列列表"""
        target_fa_list = read_fasta(target_fa)
        ref_fa_list = read_fasta(ref_fa)

        """将参考序列的各个序列分开，保存到输出文件夹的tmp文件夹中"""
        for record in ref_fa_list:
            ref_part = os.path.join(output_dir, 'tmp', f"{record.id}.fa")
            if not os.path.exists(ref_part):
                with open(ref_part, "w") as file:
                    SeqIO.write(record, file, "fasta")

        """多线程并行执行比对任务"""
        task_list = [(self.exc_path, record1, record2, os.path.join(output_dir, f"{record1.id}", f"{record2.id}"))
                     for record1, record2 in itertools.product(target_fa_list, ref_fa_list)]
        pool = multiprocessing.Pool(processes=self.max_thread)
        results = pool.map(run_unialigner, task_list)

        print('stdout:', results.stdout)
        print('stderr:', results.stderr)


class UniAlignerExt:

    def __init__(self, exe_path, threads=1):
        self.tmp_path = None
        self.exe_path = exe_path
        self.threads = threads

    def build_dir(self, fa_list, output_dir):
        """创建tmp文件"""
        os.makedirs(output_dir, exist_ok=True)
        self.tmp_path = os.path.join(output_dir, 'tmp')
        os.makedirs(self.tmp_path, exist_ok=True)
        """在tmp文件中保存ref的各个段"""
        for record in fa_list:
            ref_part = os.path.join(self.tmp_path, f"{record.id}.fa")
            if not os.path.exists(ref_part):
                with open(ref_part, "w") as file:
                    SeqIO.write(record, file, "fasta")

    def save_tmp_fasta(self, record):
        save_path = os.path.join(self.tmp_path, f"{record.id}.fa")
        if not os.path.exists(save_path):
            with open(save_path, "w") as file:
                SeqIO.write(record, file, "fasta")
        return save_path

    def align_one(self, params):
        print(params)
        record1, record2, output_dir = params
        record1_path = self.save_tmp_fasta(record1)
        record2_path = self.save_tmp_fasta(record2)
        save_out_path = os.path.join(output_dir, f"output{record1.id}.{record2.id}")
        cmd = f"{self.exe_path} --first {record1_path} --second {record2_path} -o {save_out_path}"
        subprocess.run(cmd, shell=True)
        if not os.path.exists(os.path.join(save_out_path, f"cigar.txt")):
            raise ValueError("No cigar file found!")
        with open(os.path.join(save_out_path, f"cigar.txt"), "r") as file:
            cigar = file.read()
        with open(os.path.join(output_dir, f"cigar.all.tsv"), "a") as file:
            file.write(f"{record1.id}\t{record2.id}\t{cigar}\n")
        subprocess.run(f"rm -rf {save_out_path}", shell=True)

    def align(self, query_fa, ref_fa, output_dir):
        query_fa = read_fasta(query_fa)
        ref_fa = read_fasta(ref_fa)
        self.build_dir(ref_fa, output_dir)
        task_list = [(record1, record2, output_dir) for record1, record2 in itertools.product(query_fa, ref_fa)]
        pool = multiprocessing.Pool(processes=self.threads)
        results = pool.map(self.align_one, task_list)
        print('stdout:', results)


class UniAlignerWindows:
    def __init__(self, exe_path, threads=1):
        self.tmp_path = None
        self.output_path = None
        self.exe_path = exe_path
        self.threads = threads

    def build_dir(self, output):
        """在output dir中创建tmp文件夹用于保存中间文件"""
        self.output_path = output
        self.tmp_path = join_path(output, 'tmp')
        check_and_make_path(self.tmp_path)
        with open(join_path(output, 'unialigner.paf'), 'w') as f:
            cols = ["Query.name", "Query.length", 'Query.start', 'Query.end',
                    'Target.name', 'Target.length', 'Target.start', 'Target.end',
                    'cigar_primary', 'cigar', 'cigar_recursive']
            f.write('\t'.join(cols) + '\n')

    def save_tmp_fasta(self, record):
        save_path = os.path.join(self.tmp_path, f"{record.id}.fa")
        if not os.path.exists(save_path):
            with open(save_path, "w") as file:
                SeqIO.write(record, file, "fasta")
        return save_path

    def align_one_part(self, params):
        print(params)

        """基础参数设置"""
        record1, record2, output_dir, lock = params
        step_fraction = 0.5

        """将序列按长短进行划分"""
        if len(record1) < len(record2):
            shorter_seq = record1
            longer_seq = record2
            target_name = record2.id
            query_name = record1.id
        else:
            shorter_seq = record2
            longer_seq = record1
            target_name = record1.id
            query_name = record2.id
        window_size = len(shorter_seq)
        step_size = int(window_size * step_fraction)
        chunks = sliding_split_sequence(longer_seq, window_size, step_size)
        # chunk_path = save_chunks(chunks, self.tmp_path)

        """对划分后的结果进行处理"""
        output_path = join_path(output_dir, f'{shorter_seq.id}.{longer_seq.id}')
        check_and_make_path(output_path)
        shorter_path = self.save_tmp_fasta(shorter_seq)
        check_and_make_path(output_path)
        for idx, slide in enumerate(chunks):
            chunk, start, end = slide
            chunk_path = save_chunk(slide, output_path)
            cmd = f"{self.exe_path} --first {shorter_path} --second {chunk_path[idx]} -o {output_path}"
            print(cmd)
            subprocess.run(cmd, shell=True)
            if not os.path.exists(os.path.join(output_path, f"cigar_primary.txt")):
                raise ValueError("No cigar file found!")
            with open(os.path.join(output_path, f"cigar_primary.txt"), "r") as file:
                cigar_primary = file.read()
            with open(os.path.join(output_path, f"cigar.txt"), "r") as file:
                cigar = file.read()
            with open(os.path.join(output_path, f"cigar_recursive.txt"), "r") as file:
                cigar_recursive = file.read()
            col_info = [query_name, len(shorter_seq), 0, len(shorter_seq),
                        target_name, len(longer_seq), start, end,
                        cigar_primary, cigar, cigar_recursive]
            lock.acquire()
            try:
                with open(join_path(output_dir, f"unialigner.paf"), "a") as file:
                    file.write(f"{col_info}\n")
            finally:
                lock.release()  # 释放锁
            subprocess.run(f"rm -rf {chunk_path}", shell=True)
        print("remove tmp files")
        subprocess.run(f"rm -rf {output_path}", shell=True)

    def align(self, query_fa, ref_fa, output_dir):
        """加载query和ref序列，其中query与ref中有不止一个序列"""
        query_fa = read_fasta(query_fa)
        ref_fa = read_fasta(ref_fa)
        """构造tmp文件和输出文件夹的结构"""
        self.build_dir(output_dir)

        """依次处理query与ref对，对其子对齐采用多线程并行的方式"""
        lock = multiprocessing.Manager().Lock()
        task_list = [(record1, record2, output_dir, lock) for record1, record2 in itertools.product(query_fa, ref_fa)]
        pool = multiprocessing.Pool(processes=self.threads)
        results = pool.map(self.align_one_part, task_list)
        print(results)
