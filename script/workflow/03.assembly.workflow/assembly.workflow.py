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

Log_file = 'log.txt'
FA_NAME = 'RY01_Male_xxx'

# 数据路径
VERKKO_ASSEMBLY_DIR = f'/data/home/sjwan/projects/Y-chromosome/workflow.output/data/verkko1.4/{FA_NAME}'
reference_fa = '/data/home/sjwan/projects/Y-chromosome/workflow.output/data/chm13v2.0.fa'
Y_subregion_fa = '/data/home/sjwan/projects/Y-chromosome/workflow.output/data/T2T_Y_subregion.fa'
assembly_fa = f'/data/home/sjwan/projects/Y-chromosome/workflow.output/data/verkko1.4/{FA_NAME}/assembly.fasta'
OUTPUT_DIR = f'/data/home/sjwan/projects/Y-chromosome/workflow.output/03.assembly.workflow/'
OUTPUT_DIR = join_path(OUTPUT_DIR, FA_NAME)
RAGTAG_OUTPUT = join_and_make_path(OUTPUT_DIR, 'ragtag')
PBMM2_OUTPUT = join_and_make_path(OUTPUT_DIR, 'pbmm2')
NUCFLAG_OUTPUT = join_and_make_path(OUTPUT_DIR, 'nucflag')
MINIMAP2_OUTPUT = join_path(OUTPUT_DIR, 'minimap2')

# 脚本路径

script_filter_paf_Y = '/data/home/sjwan/projects/Y-chromosome/workflow/03.assembly.workflow/filter_paf_Y.py'

logger = setup_logger(Log_file)
ragtag_assembly = RagtagScaffold(logger)
ragtag_assembly.RUN_PARAMS['reference'] = reference_fa
ragtag_assembly.RUN_PARAMS['query'] = assembly_fa
ragtag_assembly.RUN_PARAMS['output'] = RAGTAG_OUTPUT
ragtag_assembly.RUN_PARAMS['thread'] = '48'

ragtag_fa = join_path(RAGTAG_OUTPUT, 'ragtag.scaffold.fasta')
ragtag_paf = join_path(RAGTAG_OUTPUT, 'ragtag.scaffold.asm.paf')
ragtag_filter_paf = join_path(RAGTAG_OUTPUT, 'ragtag.scaffold.asm.Y.paf')
filter_paf_Y = ScriptExecutor(logger, version='bio')
filter_paf_Y.set_script_and_args(script_filter_paf_Y, [ragtag_paf, ragtag_filter_paf], {})

minimap_ragtag2reference = Minimap2_asm20(logger)
minimap_ragtag2reference.RUN_PARAMS['target'] = ragtag_fa
minimap_ragtag2reference.RUN_PARAMS['query'] = Y_subregion_fa
minimap_ragtag2reference.RUN_PARAMS['output'] = join_path(MINIMAP2_OUTPUT, 'subregion.paf')
minimap_ragtag2reference.RUN_PARAMS['thread'] = '48'

ragtag_assembly_flow = Workflow(logger)
ragtag_assembly_flow.add_software(ragtag_assembly)
ragtag_assembly_flow.add_script(filter_paf_Y)
ragtag_assembly_flow.add_software(minimap_ragtag2reference)
ragtag_assembly_flow.run(mode='DEBUG')
