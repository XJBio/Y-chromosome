import sys

sys.path.append("/data/home/sjwan/projects/Y-chromosome/utils")
from utils.software import *
from utils.build_path import *

# 输入数据
FA_NAME = 'RY01_Yao_Male_CNYAM0001'
Log_file = 'log.txt'

# 路径
fofn = f'/data/home/sjwan/projects/Y-chromosome/workflow.output/data/verkko1.4/{FA_NAME}/assembly.fofn'
assembly = f'/data/home/sjwan/projects/Y-chromosome/workflow.output/data/verkko1.4/{FA_NAME}/assembly.fasta'
with open(fofn, 'r') as f:
    reads_list = f.readlines()

OUTPUT_DIR = f'/data/home/sjwan/projects/Y-chromosome/workflow.output/03.assembly.workflow/{FA_NAME}'
VERITYMAP_OUTPUT = join_path(OUTPUT_DIR, 'veritymap')

logger = setup_logger(Log_file)
veritymap_flow = Workflow(logger)
for read in reads_list:
    veritymap = VerityMap(logger)
    veritymap.RUN_PARAMS['thread'] = '48'
    veritymap.RUN_PARAMS['output'] = VERITYMAP_OUTPUT
    veritymap.RUN_PARAMS['reads'] = read
    veritymap.RUN_PARAMS['assembly'] = assembly
    veritymap_flow.add_software(veritymap)

veritymap_flow.run('DEBUG')
