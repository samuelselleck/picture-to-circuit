from structs import Point
from skimage.draw import line
import ptc_debug
import networkx as nx
import numpy as np
import math
import circuit
from collections import defaultdict
import itertools as itr

def line_image_to_circuit(image, starts):
	
	image_graphs = __create_image_graphs(starts, image)
	circuits = __create_circuits(image_graphs)
	
	return circuits


def __create_image_graphs(starts, image):

	gig = nx.MultiGraph()
	h, w = image.shape
	
	for x in range(1, w - 1):
		for y in range(1, h - 1):
			if image[y][x] == True:
				pos = Point(x, y)
				__connect_local_node(pos, gig, image)
	
	for start in starts:
		pos = __find_edge(image, start)
		gig.add_node(pos, source=start)
	
	image_graphs = []
	
	for g in nx.connected_component_subgraphs(gig):
		if nx.get_node_attributes(g, 'source'):
			image_graphs.append(g)
			
	return image_graphs


def __connect_local_node(pos, graph, image):
	left = (-1, 0)
	up = (0, -1)
	
	leftup = True
	rightup = True
	
	dx, dy = left
	if image[pos.y + dy][pos.x + dx] == True:
			other = Point(pos.x + dx, pos.y + dy)
			graph.add_edge(pos, other)
			leftup = False
		
	dx, dy = up
	if image[pos.y + dy][pos.x + dx] == True:
			other = Point(pos.x + dx, pos.y + dy)
			graph.add_edge(pos, other)
			leftup = False
			rightup = False
	
	if leftup:
		dx, dy = (-1, -1)
		if image[pos.y + dy][pos.x + dx] == True:
			other = Point(pos.x + dx, pos.y + dy)
			graph.add_edge(pos, other)
	
	if rightup:
		dx, dy = (1, -1)
		if image[pos.y + dy][pos.x + dx] and not image[pos.y][pos.x + 1]:
			other = Point(pos.x + dx, pos.y + dy)
			graph.add_edge(pos, other)

def __find_edge(image, start):

	offset = 0
	while image[start.y][start.x + offset] == False:
		offset += 1
	pos = Point(start.x + offset, start.y)
	return pos
			
def __create_circuits(image_graphs):

	circuits_io = []
	circuit_graphs = []
	
	for image_graph in image_graphs:
		circuit_graph = __create_circuit_graph(image_graph)
		circuit = __create_circuit(circuit_graph, image_graph)
		circuits_io.append(circuit)
		circuit_graphs.append(circuit_graph)
		
	return (circuit_graphs, circuits_io)


def __create_circuit_graph(image_graph):

	circuit_graph = image_graph.copy()
	
	for n, deg in list(circuit_graph.degree()):
		if deg == 2:
			edges = list(circuit_graph.neighbors(n))
			if len(edges) == 2 and 'source' not in circuit_graph.nodes[n].keys():
				l, r = tuple(edges)
				circuit_graph.remove_node(n)
				circuit_graph.add_edge(l, r)
		
	for n, deg in list(circuit_graph.degree()):
		if deg == 1:
			other = next(circuit_graph.neighbors(n))
			if __length(__vec_between(n, other)) < 8:
				circuit_graph.remove_node(n)
				e1, e2 = circuit_graph.neighbors(other)
				circuit_graph.remove_node(other)
				circuit_graph.add_edge(e1, e2)
		
	return circuit_graph
	
def __create_circuit(circuit_graph, image_graph):

	circuit_inputs = defaultdict()
	circuit_outputs = defaultdict()
	
	for n, deg in list(circuit_graph.degree()):
		if deg == 1:
			inp = circuit.Reciever()
			circuit_outputs[n] = inp
			circuit_graph.add_node(n, line_in=inp)
			
	cycles = []
	
	triangles = [q for q in nx.enumerate_all_cliques(circuit_graph) if len(q) == 3]
	two_cycles = [[n1, n2] for n1, n2, k in circuit_graph.edges(keys=True) if k == 1]
	of_interest = triangles + two_cycles
	
	for cycle_nodes in of_interest:
		
		source_connection = next((n for n in cycle_nodes if 'source' in circuit_graph.nodes[n].keys()), None)
	
		if source_connection is not None:
			out = circuit.Sender()
			source = circuit_graph.nodes[source_connection]['source']
			circuit_inputs[source] = out
		
			for c in cycle_nodes:
				if c is not source_connection:
					circuit_graph.add_node(c, line_out=out)
		else:
			cycles.append(cycle_nodes)
		
		for n1 in cycle_nodes:
			for n2 in cycle_nodes:
				if circuit_graph.has_edge(n1, n2):
					circuit_graph.remove_edge(n1, n2)
			
		
	for cycle in cycles:
		__classify_and_create(cycle, circuit_graph, image_graph)
	
	print(str(circuit_graph))
	for sub_graph in nx.connected_component_subgraphs(circuit_graph):
		inputs = []
		outputs = []
		for node in sub_graph.nodes():
			i = sub_graph.node[node].get("line_in")
			o = sub_graph.node[node].get("line_out")
			if i is not None: 
				inputs.append(i)
			if o is not None: 
				outputs.append(o) 
			
		for inp in inputs:
			coll = circuit.OrGate()
			for out in outputs:
				out.connect_to(coll)
			coll.connect_to(inp)
			
	return (circuit_inputs, circuit_outputs)

def __classify_and_create(cycle, circuit_graph, image_graph):

	if len(cycle) == 2: #Not gate
	
		pointing = np.array([0, 0])
		for p in cycle:
			for n in image_graph.neighbors(p):
				di = __get_dir(p, n, image_graph)
				pointing = np.add(pointing, di)
			
		u, v = tuple(cycle)
		dir_vec = __norm_vec_between(u, v) #From u to v
		val = np.dot(pointing, dir_vec)
		
		if val > 0:
			u, v = v, u
			
		gate = circuit.NotGate()
		
		circuit_graph.add_node(u, line_in=gate)
		circuit_graph.add_node(v, line_out=gate)
		
	elif len(cycle) == 3: #And gate
		
		pairs = itr.combinations(cycle, r=2)
		bestVal = 10000
		for pair in pairs:
			u, v = pair
			val = nx.shortest_path_length(image_graph, u, v)
			if val < bestVal:
				bestVal = val
				bestPair = pair
			
		gate = circuit.AndGate()
		u, v = bestPair	
		circuit_graph.add_node(u, line_in=gate)
		circuit_graph.add_node(v, line_in=gate)
		w = next(n for n in cycle if n not in bestPair)
		circuit_graph.add_node(w, line_out=gate)
		
def __get_dir(start, next, image_graph):
	visited = [start]
	curr = next
	for i in range(3):
		for n in image_graph.neighbors(curr):
			if n not in visited:
				curr = n
				break
				
	return __norm_vec_between(start, curr)

def __rot90(vec):
	return np.array([vec[1], -vec[0]])
	
def __norm_vec_between(p1, p2):
	vec = __vec_between(p1, p2)
	return __norm(vec)

def __vec_between(p1, p2):
	vec = np.array([p2.x - p1.x, p2.y - p1.y])
	return vec
	
def __length(vec):
	lensq = sum(v*v for v in vec)
	return math.sqrt(lensq)
	
def __norm(vec):
	return vec / __length(vec)
	
