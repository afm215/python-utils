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
