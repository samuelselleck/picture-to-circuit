from collections import defaultdict

class Sender:
	def __init__(self):
		self.outputs = []
		
	def connect_to(self, link):
		if hasattr(link, 'recieve'):
			self.outputs.append(link)
		else:
			raise TypeError("Doesn't recieve input")
	
	def send(self, value):
		for out in self.outputs:
			out.recieve(self, value)
				
class Reciever:
	def __init__(self):	
		self.inputs = defaultdict()
	
	def recieve(self, sender, update):
		self.inputs[sender] = update
		self.on_recieve()
	
	def on_recieve(self):
		pass
		

class Gate(Sender, Reciever):
	def __init__(self):
		Reciever.__init__(self)
		Sender.__init__(self)
		self.res = None
		
	def on_recieve(self):
		res = self.process(list(self.inputs.values()))
		if self.res != res:
			self.send(res)
		self.res = res
		
	def process(self, state):
		raise NotImplemented("No Abstract Gate Behaviour")

class AndGate(Gate):
	def process(self, state):
		return all(state)
		

class NotGate(Gate):
	def process(self, state):
		return not any(state)
		
class OrGate(Gate):
	def process(self, state):
		return any(state)


		
		
