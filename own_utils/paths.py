import os 

def format_prepath(prepath: str) -> str:
    """
    Check if the prepath exists, and if it is a folder. Than retunrn the prepath with / at the end whatever the input is.
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