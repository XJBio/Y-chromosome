from math import log
import sys
import argparse

sys.path.append("/data/home/sjwan/projects/Y-chromosome/")
from utils.software import *
from utils.build_path import *
from utils.fasta import extract_Y


def load_workflow(workflow, sample):
    # 路径

    fofn = f"/data/home/sjwan/projects/Y-chromosome/workflow.output/data/verkko1.4/{sample}/fq.fofn"
    T2T = "/data/home/sjwan/projects/Y-chromosome/workflow.output/data/T2T_122XYM.fasta"
    # 读取FOFN文件中的所有读序文件路径
    with open(fofn, "r") as f:
        read_files = [line.strip() for line in f]

    # 将读序文件路径拼接成一个字符串
    read_files_str = " ".join(read_files)

    OUTPUT_DIR = f"/data/home/sjwan/projects/Y-chromosome/workflow.output/data/verkko1.4/{sample}/"

    sam = join_path(OUTPUT_DIR, "reads.minimap.sam")
    bam = join_path(OUTPUT_DIR, "reads.minimap.bam")
    sort_bam = join_path(OUTPUT_DIR, "reads.minimap.sort.bam")
    Y_bam = join_path(OUTPUT_DIR, "reads.minimap.Y.sort.bam")
    Y_reads = join_path(OUTPUT_DIR, "reads.minimap.Y.fq")

    minimap_reads = Minimap2_hifi(logger)
    minimap_reads.RUN_PARAMS["target"] = T2T
    minimap_reads.RUN_PARAMS["query"] = read_files_str
    minimap_reads.RUN_PARAMS["output"] = sam
    minimap_reads.RUN_PARAMS["thread"] = "48"
    # workflow.add_software(minimap_reads)

    samtools_sam2bam = Samtools_view_sam2bam(logger)
    samtools_sam2bam.RUN_PARAMS["thread"] = "48"
    samtools_sam2bam.RUN_PARAMS["inputsam"] = sam
    samtools_sam2bam.RUN_PARAMS["outbam"] = bam
    # workflow.add_software(samtools_sam2bam)

    samtools_sortbam = Samtools_sort_bam(logger)
    samtools_sortbam.RUN_PARAMS["thread"] = "48"
    samtools_sortbam.RUN_PARAMS["inputbam"] = bam
    samtools_sortbam.RUN_PARAMS["outbam"] = sort_bam
    # workflow.add_software(samtools_sortbam)

    samtools_index_bam = Samtools_index_bam(logger)
    samtools_index_bam.RUN_PARAMS["thread"] = "48"
    samtools_index_bam.RUN_PARAMS["inputbam"] = sort_bam
    # workflow.add_software(samtools_index_bam)
    
    samtools_view_Y = Samtools_view_name(logger)
    samtools_view_Y.RUN_PARAMS["thread"] = "48"
    samtools_view_Y.RUN_PARAMS["inputbam"] = sort_bam
    samtools_view_Y.RUN_PARAMS["name"] = 'chrY'
    samtools_view_Y.RUN_PARAMS["outbam"] = Y_bam
    # workflow.add_software(samtools_view_Y)
    
    samtools_index_Y = Samtools_index_bam(logger)
    samtools_index_Y.RUN_PARAMS["thread"] = "48"
    samtools_index_Y.RUN_PARAMS["inputbam"] = Y_bam
    # workflow.add_software(samtools_index_Y)
    
    samtools_bam2fq = Samtools_bam2fq(logger)
    samtools_bam2fq.RUN_PARAMS["thread"] = "48"
    samtools_bam2fq.RUN_PARAMS["inputbam"] = Y_bam
    samtools_bam2fq.RUN_PARAMS["outputfq"] = Y_reads
    workflow.add_software(samtools_bam2fq)
    
    remove = Remove(logger)
    remove.RUN_PARAMS["files"] = sam
    # workflow.add_software(remove)

    remove = Remove(logger)
    remove.RUN_PARAMS["files"] = bam
    # workflow.add_software(remove)
    
    remove = Remove(logger)
    remove.RUN_PARAMS["files"] = sort_bam
    # workflow.add_software(remove)
    
    remove = Remove(logger)
    remove.RUN_PARAMS["files"] = sort_bam+'.bai'
    # workflow.add_software(remove)
    
    


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="minimap for a FA type.")
    parser.add_argument("log", type=str, help="Path to save the log file")

    args = parser.parse_args()
    data_dir = "/data/home/sjwan/projects/Y-chromosome/workflow.output/data/verkko1.4"
    sample_list = os.listdir(data_dir)
    logger = setup_logger(args.log)
    sample_list.sort()
    subregion_workflow = Workflow(logger)
    for sample in sample_list:
        load_workflow(subregion_workflow, sample)
    subregion_workflow.run("RUN")
