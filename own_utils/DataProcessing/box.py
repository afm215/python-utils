import numpy as np
def randomize_box(box: 'tuple[int, int , int, int]', img_shape: 'tuple[int, int]', min_size: int, temperature: float = 0.1) -> 'tuple[int, int , int, int]':
    """
    Output a version of the input box with a noisy dimencion: the box size will vary with a difference  from 0 to temperature  * width 
    """
    x, y, width, height = box
    max_error = int(temperature * np.min((width, height))) + 1
    rnd_x, rnd_y, rnd_width, rnd_height = np.random.randint(-max_error,max_error) + x, np.random.randint(-max_error,max_error) + y, np.random.randint(-max_error,max_error) + width,np.random.randint(-max_error,max_error) + height
    rnd_x = np.min((rnd_x, img_shape[1] - min_size))
    rnd_y =  np.min((rnd_y, img_shape[0] - min_size))
    rnd_width = np.min((rnd_width, img_shape[1] - rnd_x))
    rnd_height = np.min((rnd_width, img_shape[0] - rnd_y))
    return rnd_x, rnd_y, rnd_width, rnd_height

def is_box_inside(box:'tuple[int, int , int, int]', boxref:'tuple[int, int , int, int]')-> bool:
  """
  Return True if box is inside boxref
  """
  x, y, width, height = box
  xref, yref, widthref, heightref = boxref
  return (x >= xref) and(y >= yref) and (width + x <= widthref + xref) and (height + y <= heightref + yref)

def box_contain(box:'tuple[int, int , int, int]', boxref:'tuple[int, int , int, int]')->bool:
  """
  return true if boxref in box, redondant with is_box_inside
  """
  x, y, width, height = box
  xref, yref, widthref, heightref = boxref
  return (x <= xref) and(y <= yref) and (width + x >= widthref + xref) and (height + y >= heightref + yref)

class BoxIteratorForXY():
  """
  Iterator to generate many sub windows of a picture, for a contrario approach
  """
  def __init__(self, x: int, y: int, img_shape:'tuple[int,int]', min_size: int = 7, max_size: int = 200):
    self.img_shape = img_shape
    self.max_size = np.min((np.min(img_shape), max_size))
    self.min_size = min_size

    self.x = x
    self.y = y
    self.current_width = self.min_size
    self.current_height = self.min_size
#     self.current_height = np.max((self.min_size, self.current_width//2))
    self.width_upper_limit = np.min((self.max_size, np.min((self.img_shape[1] - self.x,self.img_shape[0] - self.y )) ))
  def __iter__(self):
     return self

  def __next__(self)->'tuple[int, int , int, int]':
      if self.current_width <  self.width_upper_limit:
        box =  [self.x,self.y, self.current_width,  self.current_height]
        self.current_width += 1
        self.current_height = self.current_width
#         self.current_height = self.current_height + 1
#         if self.current_height >= np.min((self.max_size, self.img_shape[0] - self.y )) or self.current_height >= self.current_width + self.current_width // 2  :
#           self.current_height = np.max((self.min_size, self.current_width//2))
#           self.current_width += 1
        return box

      else:
          raise StopIteration
  def __len__(self):
    return self.width_upper_limit
