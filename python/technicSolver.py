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
		# orient any preferred joints on the root
		# this "solves" any attached beams
		self.root.updateAllJoints(timestamp)
		self.root.timestamp = timestamp
		for joint in self.root.joints:
			if joint.isDriver:
				linkedBeam = joint.getOtherbeam(self.root)
				linkedBeam.rotation = joint.preferredAngle
				linkedBeam.snapToJoint(joint)
				linkedBeam.timestamp = timestamp

		# traverse from whatever's linked to root to solve everything else
		beams = self.root.listLinkedBeams(None)
		while len(beams) > 0:
			beam = beams.pop()
			if beam.timestamp == timestamp:
				continue
			self.solveQuad(beam, timestamp)
			# get linked beams
			# add only the unsolved ones
			linkedBeams = beam.listLinkedBeams(None)
			unsolvedBeams = [nbeam for nbeam in linkedBeams if nbeam.timestamp < timestamp and not nbeam in beams]
			beams = beams + unsolvedBeams
			print(str(len(beams)))

	def solveQuad(self, beam, timestamp):
		# TODO: rotation about the appropriate joint isn't working right now
		# how to handle this?
		# likely that we need an "orient relative to" function


		"""
		A "Quad" has two solved beams. Determine the case and solve the remainder.
		Quad should be made up of a loop already
		Consecutive Case: solved, unsolved, unsolved, solved or solved, solved, unsolved, unsolved...
		Unconsecutive Case: s, u, s, u


		j1--b1--j2
		|       |
		b4      b2
		|       |
		j4--b3--j3

		"""

		# get quad
		print("getting quad")
		quad = self.quadCheck(beam, timestamp)
		print("quad is")
		for beam in quad:
			print(str(beam))


		if quad == None:
			print("no quad")
			return

		if quad[0].timestamp == quad[2].timestamp: # unconsecutive
			print("unconsecutive")
			unsolved1 = quad[0]
			unsolved3 = quad[2]
			solved2 = quad[1]
			solved4 = quad[3]
			if quad[0].timestamp == timestamp:
				unsolved1 = quad[1]
				unsolved3 = quad[3]
				solved2 = quad[0]
				solved4 = quad[2]
			joint1 = unsolved1.getShaderJoint(solved4)
			joint2 = unsolved1.getShaderJoint(solved2)
			joint3 = unsolved3.getShaderJoint(solved2)
			joint4 = unsolved3.getShaderJoint(solved4)

			# solve all joint positions
			joint1.position = joint1.positionRelative(solved4)
			joint2.position = joint2.positionRelative(solved2)
			joint3.position = joint3.positionRelative(solved2)
			joint4.position = joint4.positionRelative(solved4)

			# correct beam positions and orientations
			unsolved1.snapToJoint(joint1)
			unsolved1.orientation = math2d.angleToOrientation(joint2.position - joint1.position)
			unsolved3.snapToJoint(joint3)
			unsolved3.orientation = math2d.angleToOrientation(joint4.position - joint3.position)

			# update all timestamps
			unsolved1.timestamp = timestamp
			unsolved3.timestamp = timestamp
			unsolved1.updateAllJoints(timestamp)
			unsolved3.updateAllJoints(timestamp)
		else:
			"""
			sj1--s0--sj2 -> don't care about this one
			 |        |
			 u1       s1
			 |        |
			uj0--u0--sj3
			"""
			print("v")
			unsolved = []
			solved = []
			for beam in quad:
				if beam.timestamp == timestamp:
					solved.append(beam)
				else:
					unsolved.append(beam)

			if not solved[0].getSharedJoint(unsolved[1]):
				# shuffle so order matches diagram
				tmp = solved[1]
				solved[1] = solved[0]
				solved[0] = tmp

			print("solved and unsolved:")
			for beam in solved:
				print(str(beam))
			for beam in unsolved:
				print(str(beam))

			sj1 = solved[0].getSharedJoint(unsolved[1])
			sj3 = solved[1].getSharedJoint(unsolved[0])
			sj1.position = sj1.positionRelative(solved[0])
			sj3.position = sj3.positionRelative(solved[1])

			# position one end
			unsolved[0].snapToJoint(sj3)
			unsolved[1].snapToJoint(sj1)

			# get position of shared joint
			uj0 = unsolved[0].getSharedJoint(unsolved[1])
			uj0.position = math2d.circleIntersect(
				sj1.position, \
				sj3.position, \
				unsolved[0].distBetweenJoints(sj3, uj0), \
				unsolved[1].distBetweenJoints(sj1, uj0), \
				uj0.position)

			# update orientations
			unsolved[0].orientation = math2d.angleToOrientation(uj0.position - sj3.position)
			unsolved[1].orientation = math2d.angleToOrientation(uj0.position - sj1.position)

			# update all timestamps
			unsolved[0].timestamp = timestamp
			unsolved[1].timestamp = timestamp			
			unsolved[0].updateAllJoints(timestamp)
			unsolved[1].updateAllJoints(timestamp)


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
			#print("checking quad")
			for beam in quad:
				#print(str(beam.timestamp) + " " + str(timestamp))
				if beam.timestamp == timestamp:
					upToDates += 1
			if upToDates != 2:
				continue
			return quad
		return None

def generateDefaultLinkage():
	""" generates a solver with a basic linkage """
	solver = Solver()
	rootBeam = Beam(1)
	rootBeam.length = 100.0
	rootBeam.position = vec2(320.0, 240.0)
	rootBeam.rotation = math.radians(90.0)

	secondBeam = Beam(2)
	secondBeam.length = 20.0
	secondBeam.position = vec2(240.0, 240.0)
	link12 = rootBeam.joinWithBeam(40.0, secondBeam, 0.0)
	link12.isDriver = True
	link12.preferredAngle = 1.0

	thirdBeam = Beam(3)
	thirdBeam.length = 60.0
	thirdBeam.position = vec2(340.0, 178.0)
	thirdBeam.rotation = math.radians(90.0)
	link23 = thirdBeam.joinWithBeam(0.0, secondBeam, 20.0)

	fourthBeam = Beam(4)
	fourthBeam.length = 100.0
	fourthBeam.position = vec2(320.0, 141.0)
	fourthBeam.rotation = math.radians(10.0)
	link34 = fourthBeam.joinWithBeam(35.0, thirdBeam, 60.0)

	link41 = fourthBeam.joinWithBeam(0.0, rootBeam, 100.0)

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


