from joblib import Parallel, delayed
from .bash_command import run
import os 
from .paths import format_prepath,  apply_prepath_on_list

def parallelized_function_on_list(func, list_, n_jobs = 8, verbose = 1, require=None, pre_dispatch='2 * n_jobs', max_nbytes='1M'):
    result = Parallel(n_jobs = 8, verbose = verbose, resuire = require, pre_dispatch= pre_dispatch,max_nbytes=max_nbytes)(delayed(func)(elt) for elt in list_)
    return result

def remove_everything_quickly(path,n_jobs = 8, force = False):
    def remove_elt(path, force = False):
        cmd = 'rm -rf ' if force else "rm -r "
        cmd = cmd + path
        run(cmd, False)
    paths_list = apply_prepath_on_list(os.listdir(path), format_prepath(path))
    _ = parallelized_function_on_list(lambda elt: remove_elt(elt, force), paths_list, n_jobs=n_jobs, pre_dispatch='all', require="sharedmem")
