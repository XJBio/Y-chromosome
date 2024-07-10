import pandas as pd


def exist_overlap(region1, region2, gap=500):
    # 如果第一个区域在第二个区域的左边
    if region1[1] + gap < region2[0]:
        return False
    # 如果第一个区域在第二个区域的右边
    if region1[0] > region2[1] + gap:
        return False
    # 否则，存在重叠
    return True


def calculate_slope_intercept(row):
    """
    计算给定行的斜率和截距。

    参数:
    row: pd.Series, 包含 [query_start, query_end, target_start, target_end] 的行。

    返回:
    slope: float, 直线的斜率。
    intercept: float, 直线的截距。
    """
    x1, x2 = row["query_start"], row["query_end"]
    y1, y2 = row["target_start"], row["target_end"]

    # 计算斜率
    slope = (y2 - y1) / (x2 - x1)

    # 计算截距
    intercept = y1 - slope * x1

    return pd.Series({"slope": slope, "intercept": intercept})


def calculate_paf(table):
    return table.apply(calculate_slope_intercept, axis=1)


class Region:

    def __init__(self, idx, line) -> None:
        self.idx = idx
        self.name = line["query_name"]
        self.contig = [line["query_start"], line["query_end"]]
        self.region = [line["target_start"], line["target_end"]]
        self.contig_length = line["query_length"]
        self.record = []
        self.record.append(line)
        self.regions = []
        self.strand = line["strand"]

    def merge(self, line):
        if line["query_name"] != self.name:
            return False
        if exist_overlap(
            self.contig,
            [line["query_start"], line["query_end"]],
            self.contig_length * 0.01,
        ) and exist_overlap(
            self.region,
            [line["target_start"], line["target_end"]],
            self.contig_length * 0.2,
        ):

            self.contig[1] = max(line["query_end"], self.contig[1])
            self.region[1] = max(line["target_end"], self.region[1])
            self.contig[0] = min(line["query_start"], self.contig[0])
            self.region[0] = min(line["target_start"], self.region[0])
            self.record.append(line)
            return True
        return False

    def merge_region(self, other_region):
        if other_region.name != self.name:
            return False
        if exist_overlap(
            self.contig, other_region.contig, self.contig_length * 0.1
        ) or exist_overlap(self.region, other_region.region, self.contig_length * 0.1):

            self.contig[1] = max(self.contig[1], self.contig[1])
            self.region[1] = max(self.region[1], self.region[1])
            self.contig[0] = min(self.contig[0], self.contig[0])
            self.region[0] = min(self.region[0], self.region[0])
            self.regions.append(other_region)
            return True
        return False

    def merge_strand(self, line):
        if line["query_name"] != self.name:
            return False
        # 首先判断contig的两部分是否存在潜在重叠
        if exist_overlap(
            self.contig,
            [line["query_start"], line["query_end"]],
            self.contig_length * 0.1,
        ):
            pass


def merge_contigs_with_alignment(paf):
    contigs_regions = []
    paf[['k','b']] = calculate_paf(paf)
    for idx, row in paf.sort_values(by=["query_name", "query_start"]).iterrows():
        if len(contigs_regions) == 0:
            contigs_regions.append(Region(idx, row))
            continue
        if not contigs_regions[-1].merge(row):
            contigs_regions.append(Region(idx, row))
    merge_regions = []

    for region in contigs_regions:
        merge_regions.append(
            [
                region.name,
                region.region[0],
                region.region[1],
                region.region[1] - region.region[0],
                region.contig[0],
                region.contig[1],
                region.contig[1] - region.contig[0],
                len(region.record),
                region.contig_length,
            ]
        )

    merge_regions = pd.DataFrame(
        merge_regions,
        columns=[
            "query_name",
            "target_start",
            "target_end",
            "ref_length",
            "q_start",
            "q_end",
            "q_length",
            "merge_num",
            "contig_length",
        ],
    )

    return merge_regions
