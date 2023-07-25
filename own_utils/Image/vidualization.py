import numpy as np 

def make_masked_picture_red(picture, mask):
    """
    Output a the input picture such that active pixels of mask are red in the output
    """
    returned  = np.copy(picture)
    print(picture[mask >= np.max(mask)].shape)
    returned[:,:,0][mask >= np.max(mask)] = 255
    return returned
