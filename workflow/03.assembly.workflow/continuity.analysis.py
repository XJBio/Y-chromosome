import pandas as pd
import os
from tqdm import tqdm

def parse_fai(fai_file):
    regions = []
    start = 0
    end = 0 
    with open(fai_file, 'r') as f:
        for line in f:
            fields = line.strip().split('\t')
            region_name = fields[0]
            length = int(fields[1])
            end = start + length
            regions.append({
                'region_name': region_name,
                'start': start,
                'end': end,
                'length': length
            })
            start = end + 1
    return pd.DataFrame(regions)

def parse_paf(paf_file):
    data = []
    with open(paf_file, 'r') as f:
        for line in f:
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
            residue_matches = int(fields[9])
            alignment_block_length = int(fields[10])
            mapping_quality = int(fields[11])
            tags = {tag.split(':')[0]: tag.split(':')[2] for tag in fields[12:]}
            
            data.append({
                'query_name': query_name,
                'query_length': query_length,
                'query_start': query_start,
                'query_end': query_end,
                'strand': strand,
                'target_name': target_name,
                'target_length': target_length,
                'target_start': target_start,
                'target_end': target_end,
                'residue_matches': residue_matches,
                'alignment_block_length': alignment_block_length,
                'mapping_quality': mapping_quality,
                **tags
            })
    
    return pd.DataFrame(data)

if __name__ == "__main__":
    data_dir  = '/data/home/sjwan/projects/Y-chromosome/workflow.output/data/verkko1.4'
    sample_list = os.listdir(data_dir)
    sample_list.sort()
    sample_list = sample_list[::-1]
    depth_files = []
    fai = '/data/home/sjwan/projects/Y-chromosome/workflow.output/data/T2T_Y_subregion.fa.fai'
    fai_df = parse_fai(fai)
    
    for sample in tqdm(sample_list):
        paf_dir = f'/data/home/sjwan/projects/Y-chromosome/workflow.output/03.assembly.workflow/{sample}/subregion.minimap/'
        paf = os.path.join(paf_dir, f'subregion.minimap.paf')
        # paf_df = parse_paf(paf)
        # paf_df.to_csv(os.path.join(paf_dir, f'subregion.minimap.csv'), index=None)
        paf_df = pd.read_csv(os.path.join(paf_dir, f'subregion.minimap.csv'))
            # 按照 FAI 中的顺序排序 PAF 文件
        paf_df['target_name'] = pd.Categorical(paf_df['target_name'], categories=fai_df['region_name'], ordered=True)
        paf_df = paf_df.sort_values(['target_name', 'target_start'])
        paf_df.to_csv(os.path.join(paf_dir, f'subregion.minimap.sort.csv'), index=None)
    # sample_list = [sample_name.split('_')[0] for sample_name in sample_list]
    