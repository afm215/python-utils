# This is a cython code that, given a torch ImageFolder like folder path, loops through the images and check their integrity by calling the verify function from PIL
import os
import PIL.Image as Image
def check_integrity(str folder_path)->list:
  cdef list subfolders = os.listdir(folder_path) # get the subfolders names
  cdef int n_classes = len(subfolders) # get the number of classes
  cdef list images = [] # initialize an empty list to store the images paths
  cdef str image_path # declare a variable to store the image path
  cdef image # declare a variable to store the image object
  cdef list corrupted_images = []

  # loop through the subfolders
  for i in range(n_classes):
    # get the images paths in the current subfolder
    images.extend([os.path.join(folder_path, subfolders[i], f) for f in os.listdir(os.path.join(folder_path, subfolders[i]))])

  # loop through the images paths
  for image_path in images:
    # open the image with PIL
    image = Image.open(image_path)
    try:
      # call the verify function to check the integrity of the image
      image.verify()
      # print a message if the image is valid
    except:
      # print a message if the image is corrupted or invalid
      corrupted_images.append(image_path)
  return corrupted_images