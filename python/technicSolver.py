import vec2

class Solver(object)

class Beam(object):
	def __init__(self):
		self.joints = []
		self.position = vec2()
		self.rotation = 0.0
		self.length = 0.0
		self.timestamp = 0

	def getPosAlongBeam(self, posAlongBeam):
		# given a 1D position along a beam, compute the 2D world space position
		if pos > self.length or pos < 0.0:
			print("error! position length is out of bounds!")
		zero_deg = vec2(posAlongBeam, 0.0)
		return zero_deg.rotate(self.rotation) + self.position

	def joinWithBeam(self, other_beam):
		# bind two beams together based on where they intersect
		return None

class Joint(object):

	def __init__(self):
		self.position = vec2()
		self.timestamp = 0
		self.beam1 = None
		self.beam2 = None
		self.beam1_pos = -1.0
		self.beam2_pos = -2.0
		self.isDriver = False

	def positionRelative(beam):
		if self.beam1_pos is not beam and self.beam2_pos is not beam:
			return None
	    alongBeam = 0.0;
	    if beam == self.beam1) alongBeam = self.beam1_pos
	    if beam == self.beam2) alongBeam = self.beam2_pos
	    return beam.getPosAlongBeam(alongBeam)