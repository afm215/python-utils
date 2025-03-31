__package__="own_utils.ML.torch"

from torch.utils.data import Dataset
from torchvision.io import read_image
import os 
import numpy as np
from ...basics import Irange
from .random_ import random_choice as random_choice_t

class ImageFromTarDatset(Dataset):
    def __init__(self, img_dir, transform=None, target_transform=None, annotation_file = None):
        # TODO implement if needed : self.img_labels = pd.read_csv(annotations_file)
        self.img_dir = img_dir
        self.transform = transform
        self.target_transform = target_transform

    def __len__(self):
        return len(self.img_labels)

    def __getitem__(self, idx):
        img_path = os.path.join(self.img_dir, self.img_labels.iloc[idx, 0])
        image = read_image(img_path)
        # label = self.img_labels.iloc[idx, 1]
        if self.transform:
            image = self.transform(image)
        # if self.target_transform:
        #     label = self.target_transform(label)
        return image
    
class ContrastiveSampling:
    """
    Will sample successively pairs of same labels and pairs of diff labels
    """
    def _shuffle_and_split_indices(self, shuffle:bool):
        begin_with_diff_class = random_choice_t([0,1]) # 0 for same class 1 for diff
        self.same_class_dict = {} # dict that will store the idx used to create same class succession
        self.diff_class_dict={}# dict that will store the idx used to create diff class succession
        for key in self.class_dict.keys():
            indices = self.class_dict[key]
            if len(indices) % 2 != 0:
                num_same_class_samples = len(indices) // 2 + random_choice_t([0,1])
            self.same_class_dict[key] = None
            num_same_class_samples = len(indices) // 2
            if len(indices) :
                pass
        num_diff_samples = self.dataset_length // 2
        if num_diff_samples % 2 == 1:
            num_diff_samples += random_choice_t([-1,1])
        # diff_samples
        for i in Irange(0, num_diff_samples):
            pass
        
        
    
    def _reset(self):
        pass
        # self.current_index = 0
        


    def __init__(self, class_sequence, shuffle:bool = True):
        self.class_list = np.unique(class_sequence)
        self.class_dict = {}
        for class_ in self.class_list:
            self.class_dict[class_] = []
        for indx, class_ in enumerate(class_sequence):
            self.class_dict[class_].append(indx)
        self.dataset_length = len(class_sequence)
        self._reset()
    def __iter__(self):
        self._reset()
        raise NotImplementedError
        
        
        
        
    def __len__(self):
        raise NotImplementedError
    # def __next__(self):
    #     if self.current_index % 2 == 0:
    #         self.current_state = (self.current_state + 1) % 2
    #     self.current_index += 1

