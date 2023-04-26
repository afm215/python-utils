from torch.utils.data import Dataset
from torchvision.io import read_image
import os 

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
        return image, label
