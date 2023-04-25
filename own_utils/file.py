import tarfile
from .basics import format_number
from .paths import flatten_paths_recursively, format_prepath
from .bash_command import run
import os
import time 

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

def compress_to_tar(target = './', file_tree_level=0,replace_existing = False, remove_init_folder = False,  run_with_bash = True):
    """
    add target to tar file named "<target_name>.tar
    INPUTS: - target
            - file_tree_level -> default is 0 i.e. creat a tar archive of the target. If set to a number k, will convert the content at depth k in tar
            - replace_existing , if set to False, skip th ewriting if the tar file already exists
            - remove_init_folder, if True, remove the original folder after taring
            - run_with_bash, if True, use the bash command instead of the python tarfile lib
    """
    print("getting files path to tar ... ")
    content_to_tar_paths = flatten_paths_recursively(
        target, depth=file_tree_level, output_absolute_path=True
                            ) if file_tree_level > 1 else (
                                    list(
                                        map(
                                        lambda elt :format_prepath(target) +  elt, os.listdir(target)
                                        )
                                    ) if file_tree_level == 1 else [target] )

    length = len(content_to_tar_paths)
    print("creating the tars for ", length, " elements")
    for (i,elt_path) in enumerate(content_to_tar_paths):
        print("Completed at ", format_number(i / length, max_decimal_length=2),  end = '\r')
        if replace_existing or not(os.path.exists(elt_path + '.tar')):
            try:
                os.remove(elt_path + '.tar')
            except :
                pass
            if(run_with_bash):
                path_split = elt_path.split('/')
                if path_split[-1] == '':
                    path_split =  path_split[:-1] # remove the empty elt that corresponds to the last '/'
                elt_parent_path = '/'.join(path_split[:-1])
                elt_name = path_split[-1]
                cmd = "tar -cf " + elt_path + ".tar "+ "-C "+ elt_parent_path + " " + elt_name
                run(cmd, False)
            else:
                with tarfile.open(elt_path+ '.tar', "w") as tf:
                    arcname = elt_path.split('/')[-1]
                    tf.add(elt_path, arcname=arcname)
            if remove_init_folder:
                run("rm -r "+ elt_path, False )                
        else:
            print("file already existing : ", elt_path+ '.tar')
        