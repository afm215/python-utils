from tqdm import tqdm
import sys 
import os
import shutil
import random
random.seed(42)
if __name__ == "__main__":
    source = sys.argv[1]
    dest  = sys.argv [2]
    nb_elts = int(sys.argv [3])
    source_dirs = os.listdir(source)
    kept_source_dirs = random.sample(source_dirs,nb_elts)
    for dir in tqdm(kept_source_dirs):
        dir_path = os.path.join(source, dir)
        content = os.listdir(dir_path)
        dest_dir_path = os.path.join(dest, dir)
        while os.path.exists(dest_dir_path):
            dest_dir_path+="_al"
        os.mkdir(dest_dir_path)

        for i,elt in enumerate(content):
            # elt  = random.choice(content)

            src_path = os.path.join(dir_path, elt)
            dest_path = os.path.join(dest_dir_path, elt)
            shutil.copy(src_path, dest_path)
