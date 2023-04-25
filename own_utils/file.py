import tarfile
from .paths import flatten_paths_recursively
import os

def extract_file_lines_to_list(file_path:str, skip_blank_line=True):
    """
    Extract each lines of a file into a list and ignore \n
    INPUT:
        - file path : the path of the file to be considered
        - skip_blank_line : if set to True, remove the blank lines
    """
    file = open(file_path, 'r')
    raw_lines = file.readlines() 
    result = ''.join(raw_lines).split('\n')
    if skip_blank_line:
        result = list(filter(lambda elt: elt!='', result))
    return result

def compress_to_tar(target = './', file_tree_level=0,replace_existing = False, remove_init_folder = False):
    content_to_tar_paths = flatten_paths_recursively(target, depth=file_tree_level)
    
    for elt_path in content_to_tar_paths:
        if replace_existing or not(os.path.exists(elt_path + '.tar')):
            with tarfile.open(elt_path+ '.tar', "w") as tf:
                arcname = elt_path.spit('/')[-1]
                tf.add(elt_path, arcname=arcname)
        else:
            print("file already existing : ", elt_path+ '.tar')
        