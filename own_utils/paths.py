__package__="own_utils"

import os 
from .bash_command import run

def flatten_paths_recursively(root_path:str, output_absolute_path:bool=False, depth: "int|None" = None, exclusion_list:'list[str]' = [], keep_dir=False, parent_folder=None):
    """
    return the list of the paths of all the file contained in root_path
    INPUT:
    - root_path
    - output_absolute_path : if set to True, will store the absolute path
    - depth : if not None will stop the elts search at the given step
    - exclusion_list : will ignore the files whose name repsect the regexp stored
    - keep_dir : keep dir within returned list
    """
    result = []
    if os.path.isfile(root_path) or(not(depth is None) and depth == 0 ):
        if output_absolute_path:
            return [os.path.abspath(root_path)]
        return [os.path.relpath(root_path, parent_folder)]
    
    root_path = format_prepath(root_path)
    if parent_folder is None:
        parent_folder = root_path
    if keep_dir:
        result.append(root_path[:-1])
    for elt in os.listdir(root_path):
        elt_path = root_path + elt
        result += flatten_paths_recursively(elt_path, output_absolute_path, None if depth is None else depth - 1, exclusion_list=exclusion_list, keep_dir=keep_dir, parent_folder=parent_folder)
    return result

def format_prepath(prepath: str) -> str:
    """
    Check if the prepath exists, and if it is a folder. Then retunrns the prepath with / at the end whatever the input is.
    """
    assert os.path.exists(prepath), "given prepath does'nt exist : " + prepath
    assert os.path.isdir(prepath), "given prepath is not a folder : " + prepath
    return prepath if prepath[-1] == '/' else prepath + '/'

def apply_prepath_on_list(list_: list, prepath: str):
    """
    INPUT:
        - list_ is the list of file names 
        - prepath is the path we want to add before the filenames
    OUTPUT:
        - list of the prepath concatenate with each filename
    """
    prepath = format_prepath(prepath)
    return list(map(lambda elt: prepath + elt, list_))

def apply_post_str_on_list(list_:list, post_str:str):
    """
    INPUT:
        - list_ is the list of file names 
        - post_str is the str we want to add after the filenames
    OUTPUT:
        - list of the names concatenate with the post_str
    """
    return list(map(lambda elt: elt + post_str, list_))

def sort_paths_by_time(list_:list):
    """
    sort a paths list given the last modification date
    """
    new_list = list_.copy()
    new_list.sort(key=lambda x: os.path.getmtime(x))
    return new_list

def only_dirs(list_: list):
    """
    Keep only paths of directories
    """
    return list(filter(os.path.isdir, list_))

def list_only_dirs(folder_path: str):
    folder_path = folder_path.replace(" ", "\ ")
    ls_types = run ("ls -l " + folder_path +" | awk '{print $1}'", False, True, True ).split("\n")[1:-1] # get rid of the header and the last empty \n
    ls_return = run ("ls " + folder_path, False, True, True ).split("\n")[:-1]
    dirs_list = [] 
    for elt_name, elt_type in zip(ls_return, ls_types):
        if elt_type[0] == "d":
            dirs_list.append(elt_name)
    return dirs_list
    
def list_only_file(folder_path: str):
    raise NotImplementedError()

from .parallel import parallelized_function_on_list

def parallel_flatten_paths_recursively(root_path: str) -> list:
    """
    use the non parallelize version , this one suffers some serious speed issues
    """
    print("warning, use use flatten_paths_recursively instead")
    def list_child_content(path: str) -> list:
        """
        INPUT:
        - path : absolute path toward the targeted element
        OUPUT: 
        - list of all the targett content absolute paths  
        """
        if os.path.isfile(path):
            return [path]
        content = os.listdir(path)
        child_dirs = list_only_dirs(path)
        child_files = list(filter(lambda elt : not elt in child_dirs, content))
        returned_list = [os.path.join(path, elt) for elt in child_files]
        for folder in child_dirs:
            returned_list = list_child_content(os.path.join(path, folder)) + returned_list
        return returned_list

    paths_list = apply_prepath_on_list(os.listdir(root_path), root_path)
    jobs_result = parallelized_function_on_list(lambda elt: list_child_content(elt), paths_list, n_jobs=8, pre_dispatch='all', require="sharedmem")
    returned_list = []
    for result in jobs_result:
        returned_list += result
    return returned_list 

def get_relative_path(abs_path, data_path):
    """
    INPUT
    -----
    - abs_path: abs we want to extract the relative path from
    - data_path abs path that we consider to be the root path
    """
    data_path = os.path.normpath(data_path)
    splited_path = abs_path.split("/")
    for i in range(len(splited_path), 0, -1):
        if data_path in "/".join(splited_path[:-i]):
            return "/".join(splited_path[-i:])