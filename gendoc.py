#!/usr/bin/env python

# coming from https://github.com/andreww5au/PaSD-client/blob/4ea5fac6cb6b00e3aabad09a2974e0fd9b2ef949/gendocs.py

import glob
import os
from own_utils.paths import flatten_paths_recursively

"""
Generate the code documentation, using pydoc.
"""
dirname = "own_utils"
flist = list(filter(lambda elt: not "pycache" in elt, flatten_paths_recursively(dirname, False)))
# flist = glob.glob('%s/**.py' % dirname)
print(flist)
for fname in flist:
    if '__init__' not in fname and (".py" in  fname or os.path.isdir(fname)):
        os.system('pydoc -w %s' % fname)
        bname =os.path.join(os.path.dirname(fname), os.path.splitext(os.path.basename(fname))[0])+".html"  # eg 'smartbox'
        new_fname =os.path.join(os.path.dirname(fname),(bname.replace("/", ".") ))
        os.system(f"mv {fname} {new_fname}")
        os.system('mv %s %s' % (bname,new_fname))

os.system('pydoc -w %s' % dirname)
os.system('mv *.html docs')