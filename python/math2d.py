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

""" circle intersection method """
def circleIntersect(p0, r0, p1, r1, currPos):
	""" returns nearest point in circle-circle intersection to currPos """
	# http://paulbourke.net/geometry/circlesphere/
	# distance d between circle centers
	d_x = p0.x - p1.x;
	d_y = p0.y - p1.y;
	d = sqrt(d_x * d_x + d_y * d_y)
	if d > (r0 + r1): return None # no intersection; circles are too far apart
	if d < abs(r0 - r1): return None # no intersection; circle contains other

	a = (r0 * r0 - r1 * r1 + d * d) / (2.0 * d)
	h = sqrt(r0 * r0 - a * a)
	p2_x = p0_x + a * (p1_x - p0_x) / d
	p2_y = p0_y + a * (p1_y - p0_y) / d

	# circle intersect 1
	p3_1x = p2_x + h * (p1_y - p0_y) / d
	p3_1y = p2_y - h * (p1_x - p0_x) / d

	# circle intersect 2
	p3_2x = p2_x - h * (p1_y - p0_y) / d
	p3_2y = p2_y + h * (p1_x - p0_x) / d

	dist_1_x = p3_1x - curr_x
	dist_1_y = p3_1y - curr_y

	dist_2_x = p3_2x - curr_x
	dist_2_y = p3_2y - curr_y

	if (dist_2_x * dist_2_x + dist_2_y * dist_2_y) > (dist_1_x * dist_1_x + dist_1_y * dist_1_y):
		return vec2(p3_1x, p3_1y)
	else:
		return vec2(p3_2x, p3_2y)

def angleToOrientation(dir):
	# return the angle relative to horizontal needed to achieve the given vector dir
	norm = dir.norm()
	angle = math.acos(norm)
	if dir.y < 0: return angle
	else: return -angle

def vectorAlongDirection(angle):
	# return the vector direction matching the given angle relative to horizontal
	return vec2(math.cos(angle), math.sin(angle))