import numpy as np 

def crop_image(img, box):
    """
    INPUT : - img
			- bos : x, y , width , height ; x and y are the CARDINAL coordinate of the top left point of the box 
    """
    x, y, width, height = box
    box_img = img[y:y + height, x:x + width]
    return np.mean(np.abs(box_img))
