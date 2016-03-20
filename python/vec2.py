import math

class vec2(object):


	def __init__(self, x = None, y = None):
		""" initialize a 2-vector """
		if x == None or y == None:
			self.x = 0.0
			self.y = 0.0
		else:
			self.x = x;
			self.y = y;


	def __str__(self):
		return "x: " + str(self.x) + " y: " + str(self.y)


	def copy(self):
		return vec2(self.x, self.y)


	""" basic vector math """
	def __neg__(self):
		"""return negation of self"""
		return vec2(-self.x, -self.y)


	def __add__(self, other):
		return vec2(self.x + other.x, self.y + other.y)


	def __radd__(self, other):
		return other + self


	def __iadd__(self, other):
		self.x += other.x
		self.y += other.y
		return self


	def __sub__(self, other):
		return vec2(self.x - other.x, self.y - other.y)


	def __rsub__(self, other):
		return other - self


	def __isub__(self, other):
		self.x -= other.x
		self.y -= other.y
		return self


	def __mul__(self, scalar):
		return vec2(self.x * scalar, self.y * scalar)


	def __imul__(self, scalar):
		self.x *= scalar
		self.y *= scalar
		return self


	def __div__(self, scalar):
		return vec2(self.x / scalar, self.y / scalar)


	def __idiv__(self, scalar):
		self.x /= scalar
		self.y /= scalar
		return self


	""" vector operators """
	def norm(self):
		len = self.length()
		return vec2(self.x / len, self.y / len)


	def length(self):
		return sqrt(self.x * self.x + self.y * self.y)


	def rotate(self, theta):
		# a 2D rotation for CC is
		# | cos_theta -sin_theta | * [x]
		# | sin_theta  cos_theta |   [y]
		cosTheta = math.cos(theta)
		sinTheta = math.sin(theta)
		new_x = self.x * cosTheta - self.y * sinTheta
		new_y = self.x * sinTheta + self.y * cosTheta
		return vec2(new_x, new_y)


""" other vector/vector operators """
def dot(a, b):
	""" dot product of two vec2s"""
	return a.x * b.x + a.y * b.y