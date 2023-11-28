#!/usr/bin/env python
from nb_imgs_per_id_count import count_imgs_per_id
import sys
import numpy as np
if __name__ == "__main__":
    folder_path:str  = sys.argv[1]
    lengths = count_imgs_per_id(folder_path)
    unique_elts = np.unique(lengths, return_counts=True)
    print(f"Sets is composed of {len(lengths)} ids having the following numbers of images:" )
    for i in range(min(5,len(unique_elts[0]))):
        value = unique_elts[0][i]
        count = unique_elts[1][i]
        print(f"{count} ids have {value} imgs")
    if len(unique_elts[0]) > 5:
        print(".....")
        for i in range(max(5,len(unique_elts[0]) - 5), len(unique_elts[0])):
            value = unique_elts[0][i]
            count = unique_elts[1][i]
            print(f"{count} ids have {value} imgs")
                        
