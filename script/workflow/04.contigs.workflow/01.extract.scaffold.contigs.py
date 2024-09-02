import sys
import os
sys.path.append("/data/home/sjwan/projects/Y-chromosome/")

from utils.load import *
from utils.fasta import *

data_dir = '/data/home/sjwan/projects/Y-chromosome/workflow.output/data/verkko1.4'
sample_list = os.listdir(data_dir)
sample_list.sort()

for sample in sample_list:
    assembly_file = f'/data/home/sjwan/projects/Y-chromosome/workflow.output/data/verkko1.4/{sample}/assembly.fasta'
    agp_file=f'/data/home/sjwan/projects/Y-chromosome/workflow.output/03.assembly.workflow/{sample}/ragtag/ragtag.scaffold.agp'
    Y_contigs_file = f'/data/home/sjwan/projects/Y-chromosome/workflow.output/03.assembly.workflow/{sample}/ragtag/Y.contigs.fasta'
    apg_df = parse_agp(agp_file)
    agp_contigs = apg_df[apg_df['component_type'] == 'W']
    
    chrY_agp = agp_contigs[agp_contigs['object_name'].str.contains('chrY', case=False, na=False)]
    chrY_contigs = chrY_agp['component_id'].unique().tolist()
    print(sample)
    extract_contigs(assembly_file,Y_contigs_file,chrY_contigs)


    
    

