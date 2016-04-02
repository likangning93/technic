import math
import math2d
from math2d import vec2

from parts import Beam, Joint

class Solver(object):
	def __init__(self):
		self.root = None
		self.beams = []
		self.joints = []

	def solve(self, timestamp):
		return None

	def quadCheck(self, beam1, timestamp):
		""" checks if the beam specified is part of a quad
		input:
			beam1 - Beam object
			timestamp - timestamp for a "solved" beam

		returns:
			if beam1 is part of a quad with two solved beams,
			returns a list of beams in the quad.
			otherwise returns None

		some parameters to note:
			-needs to return any found quad!
			-ruh roh
			-okay: can we just yield all quad paths and check each one for validity?
		"""
		for quad in beam1.yieldQuad():
			# check if quad contains two beams with up-to-date timesteps
			upToDates = 0
			for beam in quad:
				if beam.timestamp  == timestamp:
					upToDates += 1
			if upToDates != 2:
				continue
			return quad
		return None

def generateDefaultLinkage():
	""" generates a solver with a basic linkage """
	solver = Solver()
	rootBeam = Beam()
	rootBeam.length = 100.0
	rootBeam.position = vec2(320.0, 240.0)
	rootBeam.rotation = math.radians(90.0)

	secondBeam = Beam()
	secondBeam.length = 20.0
	link12 = rootBeam.joinWithBeam(40.0, secondBeam, 0.0)
	link12.isDriver = True

	thirdBeam = Beam()
	thirdBeam.length = 60.0
	thirdBeam.position = vec2(340.0, 178.0)
	thirdBeam.rotation = math.radians(90.0)
	link23 = thirdBeam.joinWithBeam(0.0, secondBeam, 20.0)

	fourthBeam = Beam()
	fourthBeam.length = 100.0
	fourthBeam.position = vec2(320.0, 141.0)
	fourthBeam.rotation = math.radians(10.0)
	link34 = fourthBeam.joinWithBeam(35.0, thirdBeam, 60.0)

	link41 = fourthBeam.joinWithBeam(35.0, rootBeam, 100.0)

	solver.root = rootBeam
	solver.beams.append(rootBeam)
	solver.beams.append(secondBeam)
	solver.beams.append(thirdBeam)
	solver.beams.append(fourthBeam)

	solver.joints.append(link12)
	solver.joints.append(link23)
	solver.joints.append(link34)
	solver.joints.append(link41)
	return solver


