import os
import pandas as pd
import sys
sys.path.append("/data/home/sjwan/projects/Y-chromosome/utils")
from utils.software import *
from utils.build_path import *
"""
这是一个组装部分全流程：
1. Verkko组装结果（已实现）
2. 组装scaffold（使用ragtag+minimap和ragtag+nucmer）（目前先做第一个）
3. 将T2T-Y的子区域映射到scaffold的结果上，查看子区域的比对情况
4. NucFlag+VerityMap 进行错误检测
5. 使用HMMER进行特定序列的查询
"""
# 输入
FA_NAME = 'RY01_Male_xxx'


# 数据路径
VERKKO_ASSEMBLY_DIR = 'path/to/verkko/{FA_NAME}'.format(FA_NAME)
OUTPUT_DIR = 'path/to/output/{FA_NAME}'.format(FA_NAME)
RAGTAG_OUTPUT= join_and_make_path(OUTPUT_DIR, 'ragtag')
PBMM2_OUTPUT = join_and_make_path(OUTPUT_DIR, 'pbmm2')
NUCFLAG_OUTPUT = join_and_make_path(OUTPUT_DIR, 'nucflag')









