import pandas as pd
import os

from utils.load import *


def subregion_classify(fa_name):
    paf_file = f'/data/home/sjwan/projects/Y-chromosome/workflow.output/03.assembly.workflow/{fa_name}/subregion.minimap/subregion.minimap.paf'
    agp_file = f'/data/home/sjwan/projects/Y-chromosome/workflow.output/03.assembly.workflow/{fa_name}/ragtag/ragtag.scaffold.agp'

    paf = parse_paf(paf_file)
    agp = parse_agp(agp_file)
    


if __name__ == '__main__':
    data_dir = '/data/home/sjwan/projects/Y-chromosome/workflow.output/data/verkko1.4'
    sample_list = os.listdir(data_dir)
    sample_list.sort()
    sample_list = sample_list[::-1]
