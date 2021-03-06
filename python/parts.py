import math
import math2d
from math2d import vec2
import copy

class Beam(object):
	def __init__(self, int_ID):
		self.id = int_ID
		self.joints = []
		self.gears = []
		self.position = vec2() # do NOT directly modify this except on init!
		self.rotation = 0.0
		self.length = 0.0
		self.timestamp = 0

	def __str__(self):
		jointString = ""
		for joint in self.joints:
			jointString += str(joint) + " "
		return "beam ID " + str(self.id) + " joints: " + jointString


	def getPosAlongBeam(self, posAlongBeam):
		""" given a 1D position along a beam, compute the 2D world space position """
		if posAlongBeam > self.length or posAlongBeam < 0.0:
			print("error! position length " + str(posAlongBeam) + " is out of bounds!")
			print("this beam's length is " + str(self.length))
		zero_deg = vec2(posAlongBeam, 0.0)
		return zero_deg.rotate(self.rotation) + self.position

	def getNearestPosAlongBeam(self, worldPos):
		"""
		Given a world position, return the parametric position along the line to
		the nearest point along the line. Based on mathematics here:
		http://paulbourke.net/geometry/pointlineplane/
		"""
		# algorithm assumes line defined by two points
		x1 = self.position.x
		y1 = self.position.y
		p2 = self.getPosAlongBeam(self.length)
		x2 = p2.x
		y2 = p2.y
		x3 = worldPos.x
		y3 = worldPos.y
		# u is the parametric distance of the nearest point on the line
		u = ((x3 - x1) * (x2 - x1) + (y3 - y1) * (y2 - y1)) / (self.length * self.length);
		return u # unclamped, so we know what's going on

	def onBeam(self, worldPos, dist):
		"""
		Given a world position and an epsilon dist, check if the world
		position qualifies as being "on the line." If so, return the parametric
		position of the closest point to worldPos along the line.
		"""
		t = self.getNearestPosAlongBeam(worldPos)
		if t < 0.0:
			if (worldPos - self.position).length() < dist: return 0.0
			else: return None
		if t > 1.0:
			endPos = self.getPosAlongBeam(self.length)
			if (worldPos - endPos).length() < dist: return 1.0
			else: return None
		# get the position
		nearestPos = self.getPosAlongBeam(t * self.length)
		if (worldPos - nearestPos).length() < dist: return t
		else: return None


	def updateAllJoints(self, timestamp):
		""" update positions and timestamps of all linked beams """
		for joint in self.joints:
			joint.timestamp = timestamp
			joint.position = joint.positionRelative(self)

	def joinByWorldPos(self, otherBeam, worldPos, dist):
		"""
		Join the two beams together if worldPos falls along both.
		"""
		posAlongSelf = self.onBeam(worldPos, dist)
		posAlongOther = otherBeam.onBeam(worldPos, dist)
		#print(str(posAlongSelf) + " " + str(posAlongOther))
		if not posAlongSelf or not posAlongOther:
			return None

		posAlongSelf *= self.length
		posAlongOther *= otherBeam.length
		newJoint = self.joinWithBeam(posAlongSelf, otherBeam, posAlongOther)
		newJoint.position = worldPos
		return newJoint


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
			#print("looking at " + str(beam_beams[0]) + " . path so far is length " + str(len(pathCandidate)))

			# bottomed out. check for valid condition
			if len(pathCandidate) == 5:
				#print("bottomed out")
				pathCandidate.pop()
				#beam_beams[0].position = vec2()
				#print(str(beam_beams[0]))
				#print(str(self))
				if beam_beams[0] is self:
					#print("success!")
					yield [pair[0] for pair in pathCandidate]
				continue

			# exhausted this node
			if len(beam_beams[1]) == 0:
				pathCandidate.pop()
				continue

			# go deeper
			next_beam = beam_beams[1].pop()
			pathCandidate.append([next_beam, next_beam.listLinkedBeams(beam_beams[0])])

	def distBetweenJoints(self, j1, j2):
		""" get the linear distance along this beam between the two joints given """
		if j1 not in self.joints:
			return None
		if j2 not in self.joints:
			return None
		return abs(j1.getDistanceAlongBeam(self) - j2.getDistanceAlongBeam(self))

	def snapToJoint(self, joint):
		""" given a joint along this beam, position the beam according to the joint """
		# get direction from joint to end of beam
		directionToEnd = -math2d.vectorAlongDirection(self.rotation)
		self.position = joint.position + (directionToEnd * joint.getDistanceAlongBeam(self))

	def snapToPos(self, worldPos, posAlong):
		""" given a world position and position along this beam, position the beam """
		# get direction from joint to end of beam
		directionToEnd = -math2d.vectorAlongDirection(self.rotation)
		self.position = worldPos + (directionToEnd * posAlong)

	def snapToJoints(self, joint1, joint2):
		""" 
		Given two positioned joints along this beam, orient the beam.
		Prioritize joint1
		"""
		# figure out how to point
		nearJoint = joint1
		farJoint = joint2
		if joint1.getDistanceAlongBeam(self) > joint2.getDistanceAlongBeam(self):
			nearJoint = joint2
			farJoint = joint1

		direction = farJoint.position - nearJoint.position
		rotation = math2d.angleToOrientation(direction)

		# orient the beam
		self.rotation = rotation

		# snap it to the nearJoint
		self.snapToJoint(joint1)

	def getLinkableGears(self):
		# list all gears linkable on this beam
		# linkable gears are those on it or on a joint shared with an adjacent
		# excepting gears rigid-linked to this beam
		gears = []
		for gear in self.gears:
			if gear.opt_rigidBeam is not self:
				gears.append(gear)
		linkedBeams = self.listLinkedBeams(None)
		for beam in linkedBeams:
			for gear in beam.gears:
				if gear.opt_rigidBeam or gear.opt_freeBeam:
					# check if either of those two is this one
					if gear.opt_rigidBeam is not self and gear.freeBeam is self:
						gears.append(gear)
					elif gear.opt_freeBeam is self:
						gears.append(gear)
						
		return gears


class Joint(object):

	def __init__(self):
		self.position = vec2()
		self.timestamp = 0
		self.beam1 = None
		self.beam2 = None
		self.isPrismatic = False # determines if this is a prismatic joint.

		# rotational joint parameters
		self.beam1_pos = -1.0
		self.beam2_pos = -2.0
		self.preferredAngle = 0.0
		self.isDriver = False

		# debug
		self.color = (255, 0, 0)

	def positionRelative(self, beam):
		""" get the position of this joint along an input beam """
		if self.beam1 is not beam and self.beam2 is not beam:
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

	def getDistanceAlongBeam(self, beam):
		if self.beam1 is beam: return self.beam1_pos
		if self.beam2 is beam: return self.beam2_pos
		return None 

	def positionOnJoint(self, position, dist):
		return (self.position - position).length() < dist

	def delink(self):
		if self.beam1:
			self.beam1.joints.remove(self)
		if self.beam2:
			self.beam2.joints.remove(self)

class Gear(object):
	def __init__(self, int_ID):
		self.id = int_ID
		self.position = vec2()
		self.radius = 0.0
		self.freeBeam_pos = -1.0
		self.opt_rigidBeam_pos = -1.0
		self.opt_freeBeam_pos = -1.0
		self.opt_rigidBeam_dRotation = 0.0
		self.rotation = 0.0

		self.freeBeam = None
		self.opt_rigidBeam = None # optional beam whose orientation is rigidly linked to this
		self.opt_freeBeam = None # optional secondary free beam
		self.neighbors = []
		self.timestamp = 0

	def positionOnGear(self, pos):
		dist = (pos - self.position).length()
		return abs(dist - self.radius) < 3.0

	def delink(self):
		if self.freeBeam:
			self.freeBeam.gears.remove(self)
		if self.opt_rigidBeam:
			self.opt_rigidBeam.gears.remove(self)
		if self.opt_freeBeam:
			self.opt_freeBeam.gears.remove(self)
		for gear in self.neighbors:
			gear.neighbors.remove(self)

	def touching(self, center, radius):
		dist = (self.position - center).length()
		return abs(dist - (self.radius + radius)) < 3.0

	def getSharedBeam(self, gear):
		if self.freeBeam is gear.freeBeam:
			return self.freeBeam
		if self.freeBeam is gear.opt_rigidBeam:
			return self.freeBeam
		if self.freeBeam is gear.opt_freeBeam:
			return self.freeBeam
		if self.opt_rigidBeam is not None:
			if self.opt_rigidBeam is gear.freeBeam:
				return self.opt_rigidBeam
			if self.opt_rigidBeam is gear.opt_rigidBeam:
				return self.opt_rigidBeam
			if self.opt_rigidBeam is gear.opt_freeBeam:
				return self.opt_rigidBeam
		if self.opt_freeBeam is not None:
			if self.opt_freeBeam is gear.freeBeam:
				return self.opt_freeBeam
			if self.opt_freeBeam is gear.opt_rigidBeam:
				return self.opt_freeBeam
			if self.opt_freeBeam is gear.opt_freeBeam:
				return self.opt_freeBeam							

	def solve(self, timestamp):
		# can't start solving if this isn't being driven by a beam's orientation
		if not self.opt_rigidBeam or self.timestamp == timestamp:
			return

		# update this joint to match the beam that drives it
		self.rotation = self.opt_rigidBeam.rotation
		self.timestamp = timestamp

		# do an iterative depth first traversal of all linked gears
		# - everything in the "to expand" queue is "up to date"
		gearsToExpand = [self]
		while len(gearsToExpand) > 0:
			gear = gearsToExpand.pop()
			for neighbor in gear.neighbors:
				if neighbor.timestamp != timestamp:
					neighbor.timestamp = timestamp
					# get local rotations to the shared beam
					sharedBeam = gear.getSharedBeam(neighbor)
					gearLocalRotation = gear.rotation - sharedBeam.rotation

					neighborLocalRotation = -gearLocalRotation * (gear.radius / neighbor.radius)
					neighbor.rotation = neighborLocalRotation + sharedBeam.rotation

					gearsToExpand.append(neighbor)

			# update any unsolved beams attached to this
			if gear.opt_rigidBeam and gear.opt_rigidBeam.timestamp != timestamp:
				# reposition
				commonJoint = gear.opt_rigidBeam.getSharedJoint(gear.freeBeam)
				commonJoint.position = gear.freeBeam.getPosAlongBeam(gear.freeBeam_pos)
				gear.opt_rigidBeam.snapToJoint(commonJoint)
				# orient
				gear.opt_rigidBeam.rotation = gear.rotation #- gear.opt_rigidBeam_dRotation# + math.pi / 2.0
				gear.opt_rigidBeam.timestamp = timestamp
