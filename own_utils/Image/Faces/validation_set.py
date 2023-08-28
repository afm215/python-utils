
import os 
import pickle
import numpy as np
from tqdm import tqdm
import io
from PIL import Image
from ..bin_util import convert_img_to_bin


def extract_insightface_bin_data(path):
    import mxnet as mx
    imgs_b, labels = pickle.load(open(path, "rb"), encoding="bytes")
    datas = []

    length = len(imgs_b)
    print(f"extracting {length} imgs")
    for i, img_b in enumerate(tqdm(imgs_b)):
        img = mx.image.imdecode(img_b).asnumpy()
        img  = Image.fromarray(img.astype(np.uint8))
        img_name = f"img_{i}.png"
        datas.append([img_name, img])
    return datas, labels
    
    
def prepare_validation_set_conversion(imgs_dir, pairs_file):
    """
    img_dir a folder containing either directly imgs files or folders.
    If img_dir contains files, the pairs_file should contained the images  name that should follow this format : <id1>_<img_idx>.<file_extension> <id2>_<img_idx>.<file_extension>
    If not, the folders structure should be 
    ---DATAROOT
        |
        ---folder_id
            |
            --- <img_name>_<img_idx>
    and the pair file should contain lines with the following format <folder_id_1>_<img_idx>.alias <folder_id_2>_<img_idx>.alias
    """
    def get_image_path(folder,image_name):
        DataSetType = "Hierarchical" if ".alias" in image_name else "Flattened" 
        if DataSetType == "Hierarchical":
            splitted_image_name = image_name.split("_")
            parent_folder, img_alias = "_".join(splitted_image_name[:-1]), splitted_image_name[-1]
            img_idx = int(img_alias.split(".")[0])
            # parent_folder = parent_folder.replace("-", "_")
            prepath = os.path.join(folder, parent_folder)
            image_true_name = sorted(os.listdir(prepath), key = lambda elt: int(".".join(elt.split('.')[:-1]).split('_')[-1]))[img_idx]#sorted(os.listdir(prepath)[img_idx] )
            return  os.path.join(prepath, image_true_name)
        elif DataSetType == "Flattened":
            return os.path.join(folder, image_name)
        else:
            raise NotImplementedError(f"DatasetType {DataSetType} is not implemented")
    
    pairs = open(pairs_file, "r").readlines()
    imgs_list = []
    labels = np.zeros(len(pairs), dtype=bool)
    print(f"loading {len(pairs)} pairs")
    for i, pair in enumerate(tqdm(pairs)):
        if pair[-1] == "\n":
            pair = pair[:-1]
        pair_1, pair_2 = pair.split(' ')
        image_1_path = get_image_path(imgs_dir, pair_1)
        image_2_path = get_image_path(imgs_dir, pair_2)
        id1 = "_".join(pair_1.split("_")[:-1])
        id2 = "_".join(pair_2.split("_")[:-1])
        if id1 == id2:
            labels[i] = 1
        else:
            labels[i] = 0
            
        imgs_list.append(convert_img_to_bin(Image.open(image_1_path)))
        imgs_list.append(convert_img_to_bin(Image.open(image_2_path)))
    return imgs_list, labels

def write_validation_data_for_adaface(imgs_list, labels, output_file_name:str):
    np_imgs_list = [img for img in imgs_list]

    with open(output_file_name, 'wb') as file:
        # A new file will be created
        bin_ = pickle.dumps((np_imgs_list, labels), -1)
        file.write(bin_)
        file.flush()
    # A new file will be created
def convert_test_set(test_dir: str, pair_file: str, output_file_name="validation.bin"):
    """
    img_dir a folder containing either directly imgs files or folders.
    If img_dir contains files, the pairs_file should contained the images  name that should follow this format : <id1>_<img_idx>.<file_extension> <id2>_<img_idx>.<file_extension>
    If not, the folders structure should be 
    ---DATAROOT
        |
        ---folder_id
            |
            --- <img_name>_<img_idx>
    and the pair file should contain lines with the following format <folder_id_1>_<img_idx>.alias <folder_id_2>_<img_idx>.alias
    """

    imgs_list, labels = prepare_validation_set_conversion(test_dir, pair_file)
    write_validation_data_for_adaface(imgs_list, labels, output_file_name)