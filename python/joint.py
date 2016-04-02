import math
import math2d
from math2d import vec2
import beam

class Joint(object):

	def __init__(self):
		self.position = vec2()
		self.timestamp = 0
		self.beam1 = None
		self.beam2 = None
		self.beam1_pos = -1.0
		self.beam2_pos = -2.0
		self.isDriver = False
		self.preferredAngle = 0.0

	def positionRelative(self, beam):
		""" get the position of this joint along an input beam """
		if self.beam1_pos is not beam and self.beam2_pos is not beam:
			return None
		alongBeam = 0.0;
		if beam == self.beam1: alongBeam = self.beam1_pos
		if beam == self.beam2: alongBeam = self.beam2_pos
		return beam.getPosAlongBeam(alongBeam)

	def getCurrentAngle(self):
		return beam1.rotation - beam2.rotation

	def getOtherbeam(self, beam1):
		if self.beam1 is beam1: return self.beam2
		if self.beam2 is beam2: return self.beam1
		return None
