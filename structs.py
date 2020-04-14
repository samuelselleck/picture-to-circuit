class Point:
	def __init__(self, x, y):
		self.x = x
		self.y = y
	
	def dist_squared_to(self, other):
		if isinstance(other, Point):
			dx = self.x - other.x
			dy = self.y - other.y
			return dx*dx + dy*dy
		else:
			raise TypeError("Not a Point")
			
	def __str__(self):
		return "(x:" + str(self.x) + ", y:" + str(self.y) + ")"
	
	def __repr__(self):
		return str(self)
	
	def __eq__(self, other):
		return self.x == other.x and self.y == other.y
		
	def __hash__(self):
		return hash(self.x) + hash(self.y)
		
