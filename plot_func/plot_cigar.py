import matplotlib.pyplot as plt
import re


def plot_dotplot(cigar,out_fig):
    x = []
    y = []
    xpos = 0
    ypos = 0

    # 使用正则表达式来解析CIGAR字符串
    operations = re.findall(r'(\d+)(\D)', cigar)

    for length, op in operations:
        length = int(length)

        if op == 'M':  # 匹配或不匹配
            x.extend(range(xpos, xpos + length))
            y.extend(range(ypos, ypos + length))
            xpos += length
            ypos += length
        elif op == 'I':  # 插入到参考序列
            xpos += length
        elif op == 'D':  # 参考序列中的删除
            ypos += length

    # 绘制点阵图
    plt.scatter(x, y, marker='o', s=1)
    plt.title("CIGAR Dotplot")
    plt.xlabel("Position in Target")
    plt.ylabel("Position in Query")
    plt.axis('square')
    plt.savefig(out_fig)