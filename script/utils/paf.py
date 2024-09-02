import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.cm as cm

def load_paf(path):
    column_names = [
    'query_name', 'query_length', 'query_start', 'query_end', 
    'strand', 'target_name', 'target_length', 'target_start', 
    'target_end', 'num_matching', 'block_length', 'mapping_quality'
    ]
    columns_to_use = list(range(len(column_names)))
    paf_df = pd.read_csv(path, sep='\t', header=None, names=column_names, usecols=columns_to_use)
    return paf_df

    