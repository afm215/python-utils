import os
import numpy as np
def count_imgs_per_id(str folder_path)->list:
  cdef list dirs = os.listdir(folder_path)
  cdef unsigned int[:] lengths = np.uint32(np.zeros(len(dirs)))


  # loop through the subfolders
  for i, dir in enumerate(dirs):
    # get the images paths in the current subfolder
    
    lengths[i] = len(os.listdir(os.path.join(folder_path,dir)))
  return list(lengths)