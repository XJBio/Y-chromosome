import pysam
import os

def read_fasta(file_path):
    sequences = {}
    fa = pysam.Fastafile(file_path)
    for key in fa.references:
        sequences[key] = fa.fetch(key)
    fa.close()
    return sequences

def search_Y(fa_data):
    for key in fa_data:
        if 'chrY' in key:
            return key, fa_data[key]
    return 'N', 'X'

def extract_Y(file_path, output_path):
    Y_name, hap1_Y = search_Y(read_fasta(file_path))
    with open(
        os.path.join(output_path), "w"
    ) as f:
        f.write(f">{Y_name}\n")
        f.write(hap1_Y + "\n")

