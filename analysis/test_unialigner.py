import sys

sys.path.append("/mnt/d/projects/Y-chromosome")
from utils.tools import UniAlignerWindows
from utils.get_args import get_args_unialigner

if __name__ == '__main__':
    args = get_args_unialigner()

    align = UniAlignerWindows("/root/unialigner/tandem_aligner/build/bin/tandem_aligner", args.thread)

    align.align(args.query, args.target, args.output)
