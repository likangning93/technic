import math
import math2d
from math2d import vec2

class Beam(object):
	def __init__(self):
		self.joints = []
		self.position = vec2()
		self.rotation = 0.0
		self.length = 0.0
		self.timestamp = 0

	def __str__(self):
		return "beam from: " + str(self.position) + " to " + str(self.getPosAlongBeam(self.length)) 


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

	def listLinkedBeams(self, other):
		""" returns a list of beams linked to this beam, excluding other """
		return [joint.getOtherbeam(self) for joint in self.joints if joint.getOtherbeam(self) is not other]

	def yieldQuad(self):
		"""
		Yield all quad paths leading back to this beam.
		pathCandidate -> stack of beam objects and linked beams, starting with this
		"""
		pathCandidate = [[self, self.listLinkedBeams(None)]]
		while len(pathCandidate) > 0:
			beam_beams = pathCandidate[-1] # peek

			# bottomed out. check for valid condition
			if len(pathCandidate) == 4:
				if beam_beams[0] == self:
					yield [pair[0] for pair in pathCandidate]
				pathCandidate.pop()
				continue

			# exhausted this node
			if len(beam_beams[1]) == 0:
				pathCandidate.pop()
				continue

			# go deeper
			next_beam = beam_beams[1].pop()
			if len(pathCandidate) == 3:
				pathCandidate.append([next_beam, None])
			else:
				pathCandidate.append([next_beam, next_beam.listLinkedBeams(beam_beams[0])])


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
		if self.beam2 is beam1: return self.beam1
		return None
