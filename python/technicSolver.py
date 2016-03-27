import math
import math2d
from math2d import vec2

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
		"""
		# Nested For depth-limited DFS with path reconstruction
		# for every beam linked to beam1:
		#	for every beam linked to beam2:
		#		for every beam linked to beam3:
		#			for every beam linked to beam4:
		#				check quad condition
		#				return beam1, beam2, beam3, beam4 as a list

		# Iterative depth-limited DFS with reconstruction
		# datastructures:
		#	pathCandidate -> stack of (beam, idxToExploreNext)
		# push (beam1, 0) onto pathCandidate		
		# while len(pathCandidate) > 0
		# 	(currBeam, idx) = peek at pathCandidate
		# 	if pathCandidate is at max length, check quad condition:
		#		if condition holds, clean pathCandidate and return
		#		else pop from pathCandidate
		# 	else update top of pathCandidate and push another tuple on

		pathCandidate = [beam1]
		pathIndices = [0]

		while len(pathCandidate) > 0:
			if len(pathCandidate) == 4:
				# check quad condition
			else:
				jointIdx = pathIndices[-1]
				endBeam = pathCandidate[-1]
				# check if we're out of nextBeams at this candidate
				if jointIdx >= len(endBeam.joints):
					pathCandidate.pop()
					continue

				nextBeam = endBeam.joints[jointIdx].getOtherBeam[endBeam]
				# check sanity of nextBeam:
				#	-can't already be in the list

				pathIndices[-1] += 1
				pathCandidate.append[nextBeam]
				pathIndices.append[0]

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


class Beam(object):
	def __init__(self):
		self.joints = []
		self.position = vec2()
		self.rotation = 0.0
		self.length = 0.0
		self.timestamp = 0

	def getPosAlongBeam(self, posAlongBeam):
		# given a 1D position along a beam, compute the 2D world space position
		if posAlongBeam > self.length or posAlongBeam < 0.0:
			print("error! position length " + str(posAlongBeam) + " is out of bounds!")
			print("this beam's length is " + str(self.length))
		zero_deg = vec2(posAlongBeam, 0.0)
		return zero_deg.rotate(self.rotation) + self.position

	def getNearestPosAlongBeam(self, worldPos):
		""" http://paulbourke.net/geometry/pointlineplane/ """
		# algorithm assumes line defined by two points
		x1 = self.position.x
		y1 = self.position.y
		p2 = self.getPosAlongBeam(self.length)
		x2 = p2.x
		y2 = p2.y
		x3 = worldPos.x
		y3 = worldPos.y
		# u is the parametric distance to the nearest point on the line
		u = ((x3 - x1) * (x2 - x1) + (y3 - y1) * (y2 - y1)) / self.length * self.length;
		return u # unclamped, so we know what's going on


	def joinWithBeam(self, posHere, otherBeam, otherPos):
		""" bind two beams together given a length along each
		input: 
			posHere - float position along this beam
			otherBeam - pointer to other Beam object
			otherPos - float position along other beam
		returns:
			new joint binding the two beams
		"""

		# make sure these two beams aren't already joined
		if self.getSharedJoint(otherBeam) is not None:
			print("error! beams are already joined!")
			return
		# check positions
		if posHere > self.length or posHere < 0.0:
			print("error! position length " + str(posHere) + " is out of bounds!")
			print("this beam's length is " + str(self.length))
			return
		if otherPos > otherBeam.length or otherPos < 0.0:
			print("error! position length " + str(otherPos) + " is out of bounds!")
			print("this beam's length is " + str(otherBeam.length))
			return
		# create new joint
		newJoint = Joint()
		newJoint.beam1 = self
		newJoint.beam2 = otherBeam
		newJoint.beam1_pos = posHere
		newJoint.beam2_pos = otherPos
		newJoint.timestamp = self.timestamp
		newJoint.position = self.getPosAlongBeam(posHere)
		self.joints.append(newJoint)
		otherBeam.joints.append(newJoint)
		return newJoint

	def getSharedJoint(self, otherBeam):
		""" find the joint shared between these two beams, if any
		input:
			otherBeam - pointer to other Beam object
		returns:
			shared joint, if any. otherwise, returns None
		"""
		for joint1 in self.joints:
			for joint2 in otherBeam.joints:
				if joint1 is joint2: return joint1
		return None

	def getSolverJoint(self, timestamp):
		for joint in self.joints:
			if joint.timestamp == timestamp:
				return joint
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
