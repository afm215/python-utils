#!/usr/bin/env python

# coming from https://github.com/andreww5au/PaSD-client/blob/4ea5fac6cb6b00e3aabad09a2974e0fd9b2ef949/gendocs.py

import glob
import os
from time import sleep
from own_utils.paths import flatten_paths_recursively

"""
Generate the code documentation, using pydoc.
"""
dirname = "own_utils"
flist = list(filter(lambda elt: not "pycache" in elt, flatten_paths_recursively(dirname, False, keep_dir=True)))
# flist = glob.glob('%s/**.py' % dirname)
print(flist)
ordered_list = []
for fname in flist:
    if os.path.isdir(fname):
        ordered_list.append(fname)
    else:
        ordered_list = [fname] +  ordered_list
flist = ordered_list
print(flist)
for fname in flist:
    if '__init__' not in fname and (".py" in  fname or os.path.isdir(fname)):
        os.system('pydoc -w %s' % fname.replace("/", ".").replace(".py", ""))
os.system('mv *.html docs')
resulting_doc = os.listdir('docs')
elts_to_remove = list(filter(lambda elt: not(dirname in elt), resulting_doc))
os.system(f"cd docs/ && rm {' '.join(elts_to_remove)}")