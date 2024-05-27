import pandas as pd

def parse_fai(file_path):
    
    regions = {}
    with open(file_path, 'r') as file:
        for line in file:
            fields = line.strip().split('\t')
            region_name = fields[0]
            region_length = int(fields[1])
            region_start = int(fields[2])
            regions[region_name] = {
                "start": region_start,
                "end": region_start + region_length - 1,
                "length": region_length
            }
    return regions

def parse_and_filter_paf(file_path):
    # 解析PAF文件
    alignments = []
    with open(file_path, 'r') as file:
        for line in file:
            fields = line.strip().split('\t')
            query_name = fields[0]
            query_length = int(fields[1])
            query_start = int(fields[2])
            query_end = int(fields[3])
            strand = fields[4]
            target_name = fields[5]
            target_length = int(fields[6])
            target_start = int(fields[7])
            target_end = int(fields[8])
            matching_bases = int(fields[9])
            alignment_block_length = int(fields[10])
            mapq = int(fields[11])
            alignment = {
                "query_name": query_name,
                "query_length": query_length,
                "query_start": query_start,
                "query_end": query_end,
                "strand": strand,
                "target_name": target_name,
                "target_length": target_length,
                "target_start": target_start,
                "target_end": target_end,
                "matching_bases": matching_bases,
                "alignment_block_length": alignment_block_length,
                "mapq": mapq
            }
            alignments.append(alignment)
    
    # 转换为DataFrame并排序
    df = pd.DataFrame(alignments)
    df.sort_values(by=["query_name", "query_start", "query_end", "mapq"], ascending=[True, True, True, False], inplace=True)

    return df


