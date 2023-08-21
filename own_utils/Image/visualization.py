import numpy as np 
from PIL import Image

import matplotlib as plt 

def draw_boxes(img, boxes):
    """
    Display img and draw the boxes on it
    """
    # load the image
    data = img
    # plot the image
    plt.imshow(data)
    # get the context for drawing boxes
    ax = plt.gca()
    # plot each box
    for result in boxes:
        # get coordinates
        x, y, width, height = result
        # create the shape
        rect = plt.Rectangle((x, y), width, height, fill=False, color='orange')
        # draw the box
        ax.add_patch(rect)
    # show the plot
    plt.show()

def make_masked_picture_red(picture: np.ndarray, mask: np.ndarray)->np.ndarray:
    """
    Output a the input picture such that active pixels of mask are red in the output
    """
    returned  = np.copy(picture)
    print(picture[mask >= np.max(mask)].shape)
    returned[:,:,0][mask >= np.max(mask)] = 255
    return returned

def spatially_depending_thresholding(img: np.ndarray, areas_list: 'list[tuple[int]]', thresholds_list: 'list[float]', direction:str = "horizontally")->np.ndarray:
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

def visualize_imgs_list_as_grid(list_:'list[Image.Image] | list[tuple[str, Image.Image]]') -> None:
  import textwrap
  """
    Plot the list_ in matpltolib. list_ can be a lust of PIL Image or a liste of tuples  key(i.e. an image title) / Image  
  """
  def get_squared_dim_couple(length):
    squared_rounded_l = int(np.round(np.sqrt(length)))
    if length % squared_rounded_l == 0:
      return (squared_rounded_l, length//squared_rounded_l)

    return (squared_rounded_l, length//squared_rounded_l + 1)
  grid_size = get_squared_dim_couple(len(list_))
  figsize=(3.5 * grid_size[1], 3.5 * grid_size[0])
  f, axs = plt.subplots(grid_size[0],grid_size[1], figsize=figsize)
  axs = axs.flatten()
  for elt, ax in zip(list_, axs):
    if type(elt) == tuple:
      key, img = elt
    else:
      key, img = None, elt
    if key is not None:
      key = "\n".join(textwrap.wrap(key, 40))
      ax.title.set_text(key)
    ax.imshow(img)
  f.tight_layout()
  plt.show()
