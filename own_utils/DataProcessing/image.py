import numpy as np 



def crop_image(img, box):
    """
    INPUT : - img
			- bos : x, y , width , height ; x and y are the CARDINAL coordinate of the top left point of the box 
    """
    x, y, width, height = box
    box_img = img[y:y + height, x:x + width]
    return np.mean(np.abs(box_img))

def make_masked_picture_red(picture, mask):
    """
    Output a the input picture such that active pixels of mask are red in the output
    """
    returned  = np.copy(picture)
    print(picture[mask >= np.max(mask)].shape)
    returned[:,:,0][mask >= np.max(mask)] = 255
    return returned

def spatially_depending_thresholding(img: np.ndarray, areas_list: list[tuple[int]], thresholds_list: list[float], direction:str = "horizontally"):
    """
    Apply a threshold list on area specified within area lists
    """
    returned_img = np.zeros(img.shape)
    for (area_start, area_end), threshold in zip(areas_list, thresholds_list):
        print(area_start, area_end, threshold)
        if direction == "horizontally":
            print(returned_img[: , area_start: area_end].shape)
            returned_img[: , area_start: area_end] = img[: , area_start: area_end] > threshold
        elif direction == "vertically":
            returned_img[area_start: area_end, :] = img[area_start: area_end, :] > threshold
        else:
            raise NotImplementedError("direction should be either horizontally or vertically")
    return returned_img
