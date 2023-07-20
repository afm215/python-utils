import torch
from joblib import Parallel, delayed
import cv2
import numpy as np

def apply_single_conv(img, kernel, use_torch=False):
    if use_torch:
        t_img = torch.from_numpy(img[:,:,None]).permute([2,0,1])
        t_img = t_img[None,:,:,:]
        t_kernel = torch.from_numpy(kernel[None, None, :,:])
        conv = torch.conv2d(t_img, t_kernel, padding='same')
        return conv[0].permute([1,2,0]).numpy()
    else:
        return cv2.filter2D(img,-1, kernel)

def get_conv_point_wise(kernel):
    """
    Convert the kernel so that a classical convolution with the output is equiavlent to a mutliplication point wise with th einput kernel
    """
    return np.transpose(np.fliplr(np.transpose(kernel)))
    
def apply_multiple_conv(img, filters, using_parallell = True):
    """
    Apply mutliple conv on a picture , use multithreaded version on 8 thread by default
    """
    def apply_multiple_conv_on_batch(img, all_kernels, nb_batch, batch_size, batch_id):
        if (batch_id == nb_batch - 1 ):
            filters = all_kernels[batch_id * batch_size:]
        else:
            filters = all_kernels[batch_id * batch_size:(batch_id + 1) * batch_size]
        results = []
        for kernel in filters:
            results.append(apply_single_conv(img, kernel))
        return results
    
    if using_parallell:
        nb_batch = 8
        batch_size = len(filters) // nb_batch
        results = Parallel(n_jobs=nb_batch, batch_size = 1, pre_dispatch='all', max_nbytes=None, require="sharedmem" )(delayed(lambda batch_id : apply_multiple_conv_on_batch(img, filters, nb_batch, batch_size, batch_id))(batch_id) for batch_id in range(nb_batch))
        return_result = []
        for result in results:
            return_result = return_result + result
        return return_result
        
    else:
        results = []
        for kernel in filters:
            results.append(apply_single_conv(img, kernel))
        return results
