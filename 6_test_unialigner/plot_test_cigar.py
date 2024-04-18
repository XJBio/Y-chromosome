import sys
sys.path.append("/home/sjwan/ESA/workflow/")
from plot_func.plot_cigar import plot_dotplot

cigar_path = '/home/sjwan/ESA/workflow/6_test_unialigner/output/JPZ30225/temp/h1tg000001l.chrY_chm13_PAR1/cigar_primary.txt'
with open(cigar_path,'r') as f:
    cigar_str = f.read()  # 示例CIGAR字符串


plot_dotplot(cigar_str, '/home/sjwan/ESA/workflow/6_test_unialigner/output/JPZ30225/temp/h1tg000001l.chrY_chm13_PAR1/cigar_primary.png')