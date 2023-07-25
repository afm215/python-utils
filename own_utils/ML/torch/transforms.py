import torch
from torch import nn
import numpy as np 
from torchvision.transforms.functional import rotate
import torch.nn.functional as F
from torchvision.transforms.functional import resize
from PIL import Image

def get_gaussian_kernel1d(kernel_size: int, sigma: float):
   # extracted from torchvision.transforms.functional_tensor 
    ksize_half = (kernel_size - 1) * 0.5

    x = torch.linspace(-ksize_half, ksize_half, steps=kernel_size)
    pdf = torch.exp(-0.5 * (x / sigma).pow(2))
    kernel1d = pdf / pdf.sum()

    return kernel1d

def get_gaussian_kernel2d(kernel_size, sigma, dtype: torch.dtype, device: torch.device):
  # extracted from torchvision.transforms.functional_tensor 
    kernel1d_x = get_gaussian_kernel1d(kernel_size[0], sigma[0]).to(device, dtype=dtype)
    kernel1d_y = get_gaussian_kernel1d(kernel_size[1], sigma[1]).to(device, dtype=dtype)
    kernel2d = torch.mm(kernel1d_y[:, None], kernel1d_x[None, :])
    return kernel2d



class GaussianAnysotropicBlur(nn.Module):
    """
    transform Module to apply a specific anysotropic blur.
    Will create a gaussian kernel with sigma_x variance on the x axis and sigma y on the y axis. The kernel wiull then be rotate by theta (counterclockwise)
    INPUT:
    - kernel_size : tuple
    - sigmas : tuple (sigma_x , sigma_y) 
    - theta: float : angle in degree
    -kernel_dtype : torch.dtype
    - device : torch.device = device used fir the kernel
    """
    def __init__(self, kernel_size=(9,9), sigmas:list= [10,0], theta:float=0, kernel_dtype=torch.float32, device='cpu') -> None:
      super().__init__()
      self.sigmas = sigmas
      self.kernel_size = kernel_size
      self.kernel = get_gaussian_kernel2d(kernel_size, [sigmas[0], sigmas[1]], dtype=kernel_dtype, device = device)
      self.kernel = rotate(self.kernel[None], theta)[0]
    def forward(self, img: torch.Tensor):
        return F.conv2d(img, self.kernel.repeat(img.shape[-3],1, 1,1), padding='same', groups=img.shape[-3])
    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(kernel_size={self.kernel_size},sigmas={self.sigmas})"  


class GaussianRandomAnysotropicBlur(nn.Module):
    """
    Apply a random Anysotropic blur
    """
    def __init__(self, kernel_size=(9,9), sigma_x:list= [0.1,2.0], sigma_y=[0.1,0.15]) -> None:
      super().__init__()
      self.sigma_x = sigma_x
      self.sigma_y= sigma_y
      self.kernel_size=kernel_size
    def forward(self, img: torch.Tensor):
        sigmay = np.random.rand() *( np.max(self.sigma_y) -  np.min(self.sigma_y)) + np.min(self.sigma_y)
        sigmax = np.random.rand() * (np.max(self.sigma_x) - np.min(self.sigma_x)) + np.min(self.sigma_x)
        kernel = get_gaussian_kernel2d(self.kernel_size, [sigmax, sigmay], dtype=img.dtype, device = img.device)
        theta = np.random.rand() * 360
        rotated_kernel = rotate(kernel[None, :], theta)[0]
        return F.conv2d(img, rotated_kernel.repeat(img.shape[-3],1, 1,1), padding='same', groups=img.shape[-3])
    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(kernel_size={self.kernel_size},sigma_x={self.sigma_x}, sigma_y={self.sigma_y})" 

class GaussianNoise(torch.nn.Module):
    """
    Apply Gaussian Noise
    INPUT:
    mean: float
    std: float
    """
    def __init__(self, mean:float =0, std:float=0.4) -> None:
        super().__init__()
        self.noise_mean = mean
        self.noise_std = std
    def forward(self, img: torch.Tensor):
        noise = torch.tensor(np.random.normal(self.noise_mean, self.noise_std,img.size()), device=img.device, dtype=img.dtype)
        return img + noise
    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(mean={self.noise_mean}, std={self.noise_std})"   
    
class RandomDownUpsampling(torch.nn.Module):
    def __init__(self, max_down_sample_ratio: float):
        super().__init__()
        assert max_down_sample_ratio > 1, "max_down_sample_ratio should be greater than one"
        self.max_down_sample_ratio = max_down_sample_ratio
    def forward(self, img: torch.Tensor):
        if isinstance(img, Image.Image):
            input_size = img.size
        else:
            input_size = (img.size()[-2], img.size()[-1])
        down_sample_ratio = np.random.rand() * (self.max_down_sample_ratio - 1) + 1
        target_size = (int(input_size[0] / down_sample_ratio), int(input_size[1] / down_sample_ratio))
        return resize(resize(img, target_size, antialias=True), input_size, antialias=True)
        