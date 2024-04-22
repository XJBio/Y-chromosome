import argparse


def get_args_divide():
    parser = argparse.ArgumentParser("任务划分成n份 执行其中%i的位置")
    parser.add_argument('-n', '--num', type=int)
    parser.add_argument('-i', '--index', type=int)
    args = parser.parse_args()
    return args

def get_args_sample_dir():
    parser = argparse.ArgumentParser("指定输入路径和核数")
    parser.add_argument('-t', '--thread', type=int)
    parser.add_argument('-s', '--sample', type=str)
    args = parser.parse_args()
    return args

def get_args_unialigner():
    parser = argparse.ArgumentParser("指定输入路径和核数")
    parser.add_argument('-t', '--thread', type=int)
    parser.add_argument('--query', type=str)
    parser.add_argument('--target', type=str)
    parser.add_argument('--output', type=str)
    args = parser.parse_args()
    return args