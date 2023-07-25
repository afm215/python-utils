# returned by gpt 4
from PIL import Image
import torch

def is_pil_image(img):
    return isinstance(img, Image.Image)

def is_tensor_image(img):
    return torch.is_tensor(img) and img.ndimension() == 3 and (img.size()[-2] == 3 or img.size()[-2] == 1) 

def is_image_file(filename):
    return any(filename.endswith(extension) for extension in ['.png', '.jpg', '.jpeg', '.bmp', '.tif', '.tiff'])

