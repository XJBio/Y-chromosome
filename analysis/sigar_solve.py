import pandas as pd
import numpy as np
from plot_func.plot_cigar import plot_dotplot
import re

# cigar_tsv = '/home/sjwan/ESA/workflow/6_test_unialigner/temp/cigar.all.tsv'
# cigar_tsv = "E:/data/43Y/cigar.all.tsv"
#
# data = pd.read_csv(cigar_tsv, sep='\t', header=None)
#
# data.columns = ['query', 'target', 'cigar']
#
# data = data.sort_values(by=['query', 'target'])


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
        str(match_length), str(total_length), '60'
    ]
    return '\t'.join(paf_record)


def calculate_match_percentage(cigar):
    # 正则表达式匹配CIGAR中的每个操作
    pattern = re.compile(r'(\d+)([MIDNSHPX=])')
    total_length = 0
    match_length = 0
    insert_length = 0
    delete_length = 0

    for length, operation in pattern.findall(cigar):
        length = int(length)
        total_length += length  # 累加所有操作的长度
        if operation in ('M', '='):  # 计算匹配操作的总长度
            match_length += length
        if operation in ('D'):  # 计算匹配操作的总长度
            delete_length += length
        if operation in ('I'):  # 计算匹配操作的总长度
            insert_length += length

    # 计算匹配所占的比例
    match_percentage = (match_length / total_length) if total_length > 0 else 0
    insert_percentage = (insert_length / total_length) if total_length > 0 else 0
    delete_percentage = (delete_length / total_length) if total_length > 0 else 0
    return match_percentage, insert_percentage, delete_percentage


# 示例使用
with open("E:\data\\43Y\cigar_primary.txt",'r') as f:
    cigar_string = f.read()

# cigar_string = ""
# query_name = "query_seq"
# query_length = 100
# query_start = 10
# target_name = "target_seq"
# target_length = 120
# target_start = 20
#
# paf_output = cigar_to_paf(query_name, query_length, query_start, target_name, target_length, target_start, cigar_string)
# print(paf_output)
plot_dotplot(cigar_string, 'E:\data\\43Y\show.png')
# print(calculate_match_percentage(cigar_string))
# data[['Match Rate', 'Insert Rate', 'Delete Rate']] = data['cigar'].apply(lambda x: calculate_match_percentage(x)).apply(pd.Series)
#
#
# def plot_id_plot(id, frame):
#     plot_dotplot(frame.loc[764]['cigar'], f'show{id}.png')
