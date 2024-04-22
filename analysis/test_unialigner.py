import sys
sys.path.append("/data/home/sjwan/projects/Y-chromosome/")
from utils.tools import UniAlignerWindows
from utils.get_args import get_args_unialigner

if __name__ == '__main__':
    args = get_args_unialigner()

    align = UniAlignerWindows("/data/home/sjwan/tools/unialigner/tandem_aligner/build/bin/tandem_aligner", args.thread)

    align.align(args.query, args.target, args.output)
