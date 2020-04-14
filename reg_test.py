from skimage import graph, data, io, segmentation, color, transform, util
from matplotlib import pyplot as plt
from skimage.measure import regionprops
import numpy as np
from matplotlib import colors
import skimage
    
img_res = 400

image = io.imread('tests/and.jpg')

image = util.img_as_ubyte(image)
image = color.rgb2gray(image)
image = util.invert(image)

#Flip image to horizontal and resize:
h, w = image.shape
if h > w:
	image = transform.rotate(image, 90, resize=True)
h, w = image.shape
aspect_ratio = w/h
new_size = (img_res, round(img_res*aspect_ratio))
image = transform.resize(image, new_size, anti_aliasing=True)

print(skimage)

labels = segmentation.slic(image, compactness=30, n_segments=400)
g = graph.rag_mean_color(image, labels)

fig, ax = plt.subplot()

lc = graph.show_rag(labels, g, img, ax=ax[0])

plt.show()
