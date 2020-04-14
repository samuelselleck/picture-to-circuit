from skimage import io, transform, filters
from skimage.morphology import binary_dilation, thin
from skimage.color import rgb2gray
from skimage.util import img_as_ubyte, invert
from enum import Enum
import numpy as np
import sys

from structs import Point
import line_image_to_circuit as litc
import ptc_debug

def to_circuit(image, params):

	#Debug:
	debug = params['debug']
	if debug:
		tracer = ptc_debug.Tracer()
		tracer.info['plots'] = params['debug_plots']

	#Read inverted grayscale image:
	if debug: tracer.info['original_image'] = image
	image = img_as_ubyte(image)
	image = rgb2gray(image)
	image = invert(image)
	
	#Flip image to horizontal and resize:
	h, w = image.shape
	if h > w:
		image = transform.rotate(image, 90, resize=True)
	h, w = image.shape
	aspect_ratio = w/h
	new_size = (params['img_res'], round(params['img_res']*aspect_ratio))
	image = transform.resize(image, new_size, anti_aliasing=True)
	if debug: tracer.info['inverted_grayscale_image'] = image
	
	#Binarize image with local thresholding:
	threshold = filters.threshold_local(
		image, params['img_local_threshold_size'], offset=params['img_local_threshold_offset'])
	image = image > threshold
	image = thin(image)
	
	if debug: tracer.info['threshold_image'] = image
	
	#Find circles (buttons) with hough transform:
	hough_image = binary_dilation(image)
	try_radii = params['hough_radii']
	hough_space = transform.hough_circle(hough_image, try_radii)
	_, *circles = transform.hough_circle_peaks(
		hough_space, try_radii,
		min_xdistance=params['min_start_distance'],
		min_ydistance=params['min_start_distance'],
		normalize=True,
		threshold=params['hough_threshold'])
	circles = list(zip(*circles))
	
	#Build rough graph:
	starts = [Point(x, y) for x, y, r in circles]
	one_to_one = zip(starts, circles)
	starts = __cull_close_points(starts, params['min_start_distance']) #Hough only does for separate radii
	if debug: tracer.info['source_circles'] = [c for p, c in one_to_one if any(p is s for s in starts)]
	broadcast_distance = params['temp_graph_broadcast_dist']
	circuit_graphs, circuit_io = litc.line_image_to_circuit(image, starts)
	if debug: 
		tracer.info['circuit_graphs'] = circuit_graphs
		tracer.info['circuit_io'] = circuit_io
		
	res = { 
		'circuit': circuit_io, #not correct yet
		'starts': starts
	}
	
	if debug: res['tracer'] = tracer
	
	return res

def __cull_close_points(points, min_dist):
	culled_points = []
	for p1 in points:
		to_close = []
		for p2 in points:
			if (not p1 is p2) and p1.dist_squared_to(p2) < pow(min_dist, 2):
				to_close.append(p2)
		if not [p for p in to_close if p in culled_points]:
			culled_points.append(p1)
	return culled_points
		
#Parameters:
default_params = {
	'img_res': 400, 
	'img_local_threshold_size': 35,
	'img_local_threshold_offset': -0.01,
	'hough_radii': np.arange(10, 25),
	'hough_threshold': 0.88,	
	'min_start_distance': 10, 
	'temp_graph_broadcast_dist': 10,
	'debug': True,
	'debug_plots': [3],
	'debug_circuit': True
}

if __name__ == "__main__":
	image = io.imread(sys.argv[1])
	print("running picture to circuit")
	res = to_circuit(image, default_params)
	print("picture to circuit done")
	if default_params['debug']:
		ptc_debug.plot_debug_info(res['tracer'])
		if default_params['debug_circuit']:
			circuits = res['tracer'].info['circuit_io']
			ptc_debug.truth_table(circuits)
			ptc_debug.test_circuit(circuits)
	
   


   


