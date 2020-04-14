from skimage.draw import line, circle_perimeter
from skimage import transform
from matplotlib.patches import Circle
import matplotlib.pyplot as plt
from skimage.color import gray2rgb
import numpy as np
from structs import Point
import itertools as itr

class Tracer:
	def __init__(self):
		self.info = {}

def truth_table(circuits):
	for i, circuit in enumerate(circuits):
		print("------------Circuit " + str(i) + "----------------")
		inp, out = circuit
		num_inputs = len(inp)
		for inputs in itr.product([False, True], repeat=num_inputs):
			print(str(list(inputs)) + "\t", end='')
			for j, sender in enumerate(inp.values()):
				sender.send(inputs[j])
			for reciever in out.values():
				print( " | " + str(any(reciever.inputs.values())), end='')
				
			print()
		
def test_circuit(circuits):
	
	for c in circuits:
		inp, out = c
		for i in inp.values():
			i.send(False)
		
	while True:
		for i, c in enumerate(circuits):
			print("------------Circuit " + str(i) + "----------------")
			inp, out = c
		
			print("inputs: ", end='')
			for p, s in inp.items():
				print(str(p) + " | ", end='')
			print("\noutputs: ", end='')
			for p, r in out.items():
				print(str(p) + " | ", end='')
			print()
		print("-------------------------------------------------")
		print("circuit:")
		cir = int(input())
		print("input index (left to right):")
		index = int(input())
		print("value:")
		val = input() == "1"
		
		sender = list(circuits[cir][0].values())[index]
		sender.send(val)
		
		for p, reciever in circuits[cir][1].items():
			print(str(p) + " out: " + str(any(reciever.inputs.values())))
		
		if cir == "exit":
			break
			
def plot_debug_info(tracer):

	if 1 in tracer.info['plots']:
		#Plot original image:
		plt.imshow(tracer.info['original_image'])
		
	if 2 in tracer.info['plots']:
		#Plot resized inverted grayscale:
		fig, ax = plt.subplots()
		ax.imshow(tracer.info['inverted_grayscale_image'], cmap='gray')
	
	if 3 in tracer.info['plots']:
		#Plot template graph construction:
		fig, ax = plt.subplots()
		fact = 1
		image = tracer.info['threshold_image']
		image = transform.rescale(image, fact, multichannel=False, order=0)
		image = gray2rgb(image)
		image = (image * 255).astype(np.uint8)
		__draw_circles(ax, fact, [c for c in tracer.info['source_circles']])
		for graph in tracer.info['circuit_graphs']:
				__draw_graph(graph, fact, image)
				
		ax.imshow(image)
		
	plt.show(block=True)
		
def __draw_graph(graph, factor, image):
	ofs = round(factor/2 - 0.5)
	for p1, p2 in graph.edges():
		rr, cc = line(p1.y*factor + ofs, p1.x*factor + ofs, p2.y*factor + ofs, p2.x*factor + ofs)
		image[rr, cc] = [255, 0, 0]
	for n in graph.nodes():
		if graph.nodes[n].get('line_in') is not None:
			rr, cc = circle_perimeter(n.y*factor + ofs, n.x*factor + ofs, 1*factor)
			image[rr, cc] = [0, 255, 0]
		if graph.nodes[n].get('line_out') is not None:
			rr, cc = circle_perimeter(n.y*factor + ofs, n.x*factor + ofs, 2*factor)
			image[rr, cc] = [0, 0, 255]
		
	
def __draw_circles(ax, factor, circles):
	ofs = round(factor/2 - 0.5)
	for x, y, r in circles:
		c = Circle((x*factor + ofs, y*factor + ofs), r*factor, fill=False,color=(0.20, 0.40, 1), linewidth=1)
		ax.add_patch(c)
