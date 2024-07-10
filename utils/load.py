import pandas as pd


def parse_agp(agp_file):
    contigs = []
    with open(agp_file, 'r') as f:
        for line in f:
            if line.startswith('#') or line.startswith('##'):
                continue
            fields = line.strip().split('\t')
            object_name = fields[0]
            object_start = int(fields[1])
            object_end = int(fields[2])
            part_number = int(fields[3])
            component_type = fields[4]

            if component_type == 'W':
                component_id = fields[5]
                component_start = int(fields[6])
                component_end = int(fields[7])
                orientation = fields[8]

                contigs.append({
                    'object_name': object_name,
                    'object_start': object_start,
                    'object_end': object_end,
                    'part_number': part_number,
                    'component_type': component_type,
                    'component_id': component_id,
                    'component_start': component_start,
                    'component_end': component_end,
                    'orientation': orientation
                })
            elif component_type == 'U':
                contigs.append({
                    'object_name': object_name,
                    'object_start': object_start,
                    'object_end': object_end,
                    'part_number': part_number,
                    'component_type': component_type,
                    'component_id': fields[5],
                    'component_start': None,
                    'component_end': None,
                    'orientation': None
                })
    return pd.DataFrame(contigs)


def read_fai(fai_path):
    """读取FAI文件，并返回DataFrame."""
    fai_df = pd.read_csv(fai_path, sep='\t', header=None, names=['contig', 'length', 'offset', 'linebases', 'linewidth'])
    starts = []
    ends = []
    start = 1
    end = 0
    for idx, row in fai_df.iterrows():
        end = start + row['length']
        starts.append(start)
        ends.append(end)
        start = end + 1
    fai_df['start'] = starts
    fai_df['end'] = ends 
    return fai_df


def split_contig(contig_name, length, max_size=5000000, overlap=0.25):
    """将长度超过max_size的contig分割成多个区域，并且重叠overlap比例."""
    regions = []
    step = int(max_size * (1 - overlap))
    start = 1
    while start < length:
        end = min(start + max_size, length)
        regions.append((contig_name, start, end))
        start += step
    return regions


def save_bed(regions, bed_path):
    """保存区域信息到BED文件."""
    with open(bed_path, 'w') as f:
        for contig, start, end in regions:
            f.write(f"{contig}\t{start}\t{end}\n")


def process_fai(fai_path, bed_path, max_size=5000000, overlap=0.25):
    fai_df = read_fai(fai_path)
    all_regions = []
    for _, row in fai_df.iterrows():
        contig_name = row['contig']
        length = row['length']
        if length > max_size:
            regions = split_contig(contig_name, length, max_size, overlap)
            all_regions.extend(regions)
        else:
            all_regions.append((contig_name, 0, length))
    save_bed(all_regions, bed_path)


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


def load_misasm_bed(file):
    bed_df = pd.read_csv(file, sep="\t", header=None)
    bed_df[0] = bed_df[0].apply(lambda x: x.split(":")[0])
    return bed_df.values.tolist()
