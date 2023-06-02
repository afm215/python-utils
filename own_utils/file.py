import tarfile
from .basics import format_number
from .paths import flatten_paths_recursively, format_prepath
from .bash_command import run
import os
import time 

def extract_file_lines_to_list(file_path:str, skip_blank_line=True):
    """
    Extract each lines of a file into a list and ignore \n

    INPUTS:
    -------
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

    INPUTS: 
    ------
        - target
        - file_tree_level : default is 0 i.e. creat a tar archive of the target. If set to a number k, will convert the content at depth k in tar
        - replace_existing : if set to False, skip th ewriting if the tar file already exists
        - remove_init_folder : if True, remove the original folder after taring
        - run_with_bash : if True, use the bash command instead of the python tarfile lib
    """
    print("getting files path to tar ... ", flush=True)
    content_to_tar_paths = flatten_paths_recursively(
        target, depth=file_tree_level, output_absolute_path=True
                            ) if file_tree_level > 1 else (
                                    list(
                                        map(
                                        lambda elt :format_prepath(target) +  elt, os.listdir(target)
                                        )
                                    ) if file_tree_level == 1 else [target] )

    content_to_tar_paths = list(filter(lambda elt : elt[-3:]!= 'tar', content_to_tar_paths))
    length = len(content_to_tar_paths)
    print("creating the tars for ", length, " elements", flush=True)
    for (i,elt_path) in enumerate(content_to_tar_paths):
        print("Completed at ", format_number(i / length, max_decimal_length=2),  end = '\r', flush=True)
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
                run(cmd, False, False)
            else:
                with tarfile.open(elt_path+ '.tar', "w") as tf:
                    arcname = elt_path.split('/')[-1]
                    tf.add(elt_path, arcname=arcname)
            if remove_init_folder:
                run("rm -r "+ elt_path, False , False)                
        else:
            print("file already existing : ", elt_path+ '.tar', flush=True)

def extracts_tar(path:str = './', remove_init_tar_folder = False, output_folder:str=None):
    """
    Extract the specified tar

    INPUTS:
    -------
    - path : file to ward the tar file
    - remove_init_tar_folder : If set to True, remove the file located at `path`after the extraction
    - output_folder : if None, the extracted content will be at the same level as the input filen, else the content will be deplace in output_folder 
    """
    if os.path.isfile(path):
        path_split = path.split('/')
        if output_folder is None:
            dir_path = '/'.join(path_split[:-1])
        else:
            dir_path = output_folder
            os.makedirs(dir_path, exist_ok=True)
        if path[-3:] == 'tar' :
            cmd = "tar -xf " + path + '-C' + dir_path

        elif path[-6:] == '.tar.gz':
            cmd = "tar -xzf " + path + '-C' + dir_path
        run(cmd, False)
    else:
        dir_path = format_prepath(path)
        for elt in os.listdir(dir_path):
            extracts_tar(dir_path + elt, remove_init_tar_folder, output_folder)

def copy(src_path:str, dst:str, use_rsync: bool =False, recursive = False, archive_mode=False):
    """
    Copy `src_path` to `dst`

    INPUTS:
    -------
    - src_path
    - dst
    - use_rsync: if True will run rsync else , it uses cp
    - recursive : performs recursive copy
    - archive_mode : only with rsync ! use the -a option, not compative with recursive  = True
    """
    dst = format_prepath(dst)
    core = src_path + " " + dst
    tool = "rsync " if use_rsync else "cp " 
    if recursive:
        assert archive_mode == False, "archive mode should not be uses with recursive = True"
        tool += "-r "
    if archive_mode:
        assert use_rsync, "archive mode only available with rsync"
        tool += "-a "
    cmd = tool + core
    run(cmd, False)


        