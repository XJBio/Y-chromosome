import os
import pandas as pd
import sys
import argparse
sys.path.append("/data/home/sjwan/projects/Y-chromosome/")
from utils.software import *
from utils.build_path import *
from utils.load import parse_agp, read_fai, split_contig, save_bed



def load_workflow(workflow, sample):
    
    agp = f'/data/home/sjwan/projects/Y-chromosome/workflow.output/03.assembly.workflow/{sample}/ragtag/ragtag.scaffold.agp'
    bam = f'/data/home/sjwan/projects/Y-chromosome/workflow.output/data/verkko1.4/{sample}/assembly.fasta.pbmm.sort.bam'
    fai = f'/data/home/sjwan/projects/Y-chromosome/workflow.output/data/verkko1.4/{sample}/assembly.fasta.fai'
    agp_df = parse_agp(agp)
    agp_df = agp_df[agp_df['object_name']=='chrY_RagTag']
    fai_df = read_fai(fai)
    
    output_dir = f'/data/home/sjwan/projects/Y-chromosome/workflow.output/03.assembly.workflow/{sample}/nucflag'
    check_and_make_path(output_dir)
    
    for idx, row in agp_df.iterrows():
        if row['component_type'] == 'W':
            contig_name = row['component_id']
            contig_bam = join_path(output_dir, contig_name+'.bam')
            region_bed = join_path(output_dir, contig_name+'.region.bed')
            misasm = join_path(output_dir, contig_name+'.misasm.bed')
            status = join_path(output_dir, contig_name+'.status.bed')
            toml = join_path(output_dir, contig_name+'.toml')
            img_dir = join_and_make_path(output_dir, 'image')
            
            length = fai_df[fai_df['contig'] == contig_name]['length'].iloc[0]
            region = split_contig(contig_name, length)
            save_bed(region, region_bed)
            
            os.system(f'cp /data/home/sjwan/projects/Y-chromosome/workflow.output/nucfreq/output/contig.toml {toml}')
            
            view_contig = Samtools_view_name(logger)
            view_contig.RUN_PARAMS['thread'] = '48'
            view_contig.RUN_PARAMS['name'] = contig_name
            view_contig.RUN_PARAMS['inputbam'] = bam
            view_contig.RUN_PARAMS['outbam'] = contig_bam
            
            index_contig = Samtools_index_bam(logger)
            index_contig.RUN_PARAMS['thread'] = '48'
            index_contig.RUN_PARAMS['inputbam'] = contig_bam
            
            nucflag = Nucflag(logger)
            nucflag.RUN_PARAMS['thread'] = '48'
            nucflag.RUN_PARAMS['contigbam'] = contig_bam
            nucflag.RUN_PARAMS['region'] = region_bed
            nucflag.RUN_PARAMS['toml'] = toml
            nucflag.RUN_PARAMS['imgout'] = img_dir
            nucflag.RUN_PARAMS['misasm'] = misasm
            nucflag.RUN_PARAMS['status'] = status
            
            workflow.add_software(view_contig)
            workflow.add_software(index_contig)
            workflow.add_software(nucflag)
            
    
    
    

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Ragtag for a FA type.")
    parser.add_argument("log", type=str, help="Path to save the log file")
    
    args = parser.parse_args()
    data_dir  = '/data/home/sjwan/projects/Y-chromosome/workflow.output/data/verkko1.4'
    sample_list = os.listdir(data_dir)
    sample_list.sort()
    sample_list = sample_list[::-1]
    logger = setup_logger(args.log)
    nucflag_workflow = Workflow(logger)
    for sample in sample_list:
        load_workflow(nucflag_workflow, sample)
    nucflag_workflow.run('RUN')