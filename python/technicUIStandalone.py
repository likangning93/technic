import pygame
import sys
import technicSolver
from parts import Beam, Joint
import math2d
from math2d import vec2

# help from https://www.cs.ucsb.edu/~pconrad/cs5nm/topics/pygame/drawing/

pygame.init()
clock = pygame.time.Clock() # for maintaining constant update time
screen = pygame.display.set_mode((640,480)) # open a window

bg_color = (255, 255, 255)
black = (0,0,0)
red = (255, 0, 0)
blue = (0, 0, 255)
teal = (0, 255, 255)

clickDist = 5.0

class solverTestState(object):

	def drawBeam(self, beam):
		pos = beam.position
		end = beam.getPosAlongBeam(beam.length)
		clr = black
		if beam == self.state_selectedBeam:
			clr = teal

		pygame.draw.lines(screen, clr, False, [(int(pos.x),int(pos.y)), (int(end.x),int(end.y))], 1)
		pygame.draw.circle(screen, clr, (int(pos.x), int(pos.y)), 2, 0)
		pygame.draw.circle(screen, clr, (int(end.x), int(end.y)), 2, 0)
		# draw each of the joints along this beam
		for joint in beam.joints:
			pos = joint.positionRelative(beam)
			clr = joint.color
			if joint is self.state_selectedJoint:
				clr = blue
			pygame.draw.circle(screen, clr, (int(pos.x), int(pos.y)), 6, 1)
			pygame.draw.circle(screen, clr, (int(pos.x), int(pos.y)), 2, 1)

	def drawProspectiveBeam(self):
		if self.state_mode_addBeams and self.state_mouseLastCoord is not None \
		and self.state_mouseDownCoord is not None:
			pygame.draw.lines(screen, teal, False, \
			[(int(self.state_mouseDownCoord.x),int(self.state_mouseDownCoord.y)), \
			(int(self.state_mouseLastCoord.x),int(self.state_mouseLastCoord.y))], 1)


	def __init__(self):
		# simulation state members
		self.state_mode_dragManip = False # activate by pressing d
		self.state_mode_addBeams = False # activate by pressing b
		self.state_mode_addJoints = False # activate by pressing j
		self.state_play = False

		self.state_mouseDownCoord = None
		self.state_mouseLastCoord = None

		self.state_selectedBeam = None
		self.state_selectedJoint = None
		self.state_soleStaticJoint = None
		self.nextBeamID = 5

		self.time = 1
		self.solver = technicSolver.generateDefaultLinkage()
		# get the driver joint, we need that.
		self.driverJoint = None
		for joint in self.solver.joints:
			if joint.isDriver:
				self.driverJoint = joint
				break

	def solve(self):
		if self.state_play:
			self.solver.solve(self.time)
			self.driverJoint.preferredAngle += 0.1
			self.time += 1

	def stepFwd(self):
		self.driverJoint.preferredAngle += 0.1
		self.time += 1		
		self.solver.solve(self.time)

	def stepBck(self):
		self.driverJoint.preferredAngle -= 0.1
		self.time -= 1
		self.solver.solve(self.time)

	def getClickedBeams(self, pos_vec2):
		return [beam for beam in self.solver.beams if beam.onBeam(pos_vec2, clickDist)]

	def getClickedJoints(self, pos_vec2):
		return [joint for joint in self.solver.joint if joint.positionOnJoint(pos_vec2, clickDist)]

	def addBeam(self, beam):
		self.solver.beams.append(beam)

	def deleteBeam(self, beam):
		if beam == self.solver.root:
			print("don't delete root ok?")
			return

		if beam not in self.solver.beams:
			return
		self.solver.beams.remove(beam)
		# delete all joints linked to this beam
		for joint in beam.joints:
			self.solver.joints.remove(joint)
			joint.delink()

	def addJointsOnBeams(self, pos_vec2):
		clickedBeams = self.getClickedBeams(pos_vec2)
		# generate a new joint between every pair of clicked beams
		numClicked = len(clickedBeams)
		for i in xrange(numClicked - 1):
			newJ = clickedBeams[i].joinByWorldPos(clickedBeams[i + 1], pos_vec2, clickDist)
			if newJ:
				self.solver.joints.append(newJ)

	def deleteJoint(self, joint):
		joint.delink()
		self.solver.joints.remove(joint)		

	def mousePressHandler(self, mousePos):
		mousePos_vec2 = vec2(mousePos[0], mousePos[1])
		self.state_mouseDownCoord = mousePos_vec2

		if self.state_mode_dragManip:
			return

		if self.state_mode_addBeams:
			return

		if self.state_mode_addJoints:
			# see if can add joints connecting multiple beams
			self.addJointsOnBeams(mousePos_vec2)
			return


	def mouseDragHandler(self, mousePos):
		mousePos_vec2 = vec2(mousePos[0], mousePos[1])
		self.state_mouseLastCoord = mousePos_vec2
		if self.state_mode_dragManip:
			return

		if self.state_mode_addBeams:
			# nothing to do here lol
			return

	def mouseUpHandler(self, mousePos):
		mousePos_vec2 = vec2(mousePos[0], mousePos[1])

		if self.state_mode_addBeams:
			# add a beam between mouse up and mouse down
			#print("adding beam")
			beamVec = mousePos_vec2 - self.state_mouseDownCoord
			newBeam = Beam(self.nextBeamID)
			self.nextBeamID += 1
			newBeam.position = self.state_mouseDownCoord
			newBeam.length = beamVec.length()
			newBeam.rotation = math2d.angleToOrientation(beamVec)
			self.addBeam(newBeam)

		# clear mouse coordinates, we don't care anymore
		self.state_mouseDownCoord = None
		self.state_mouseLastCoord = None

	def keyPressHandler(self, key):
		if key == pygame.K_RIGHT:
			#print("ffwd")
			self.stepFwd()

		if key == pygame.K_LEFT:
			#print("back")
			self.stepBck()

		if key == pygame.K_SPACE:
			#print("toggle pause/play")
			self.state_play = not self.state_play

		if key == pygame.K_s:
			print("changed to select and drag mode")
			self.state_mode_dragManip = True # activate by pressing d
			self.state_mode_addBeams = False # activate by pressing b
			self.state_mode_addJoints = False # activate by pressing j

		if key == pygame.K_b:
			print("changed to beam adding mode")
			self.state_mode_dragManip = False # activate by pressing d
			self.state_mode_addBeams = True # activate by pressing b
			self.state_mode_addJoints = False # activate by pressing j			

		if key == pygame.K_j:
			print("changed to joint adding mode")
			self.state_mode_dragManip = False # activate by pressing d
			self.state_mode_addBeams = False # activate by pressing b
			self.state_mode_addJoints = True # activate by pressing j			

		if key == pygame.K_DELETE:
			print("commanded to delete selection")
			if self.state_mode_dragManip:
				if self.state_selectedBeam:
					self.deleteBeam(self.state_selectedBeam)
					self.state_selectedBeam = None
				if self.state_selectedJoint:
					self.deleteJoint(self.state_selectedJoint)
					self.state_selectedJoint = None
		pass

test = solverTestState()

# main drawing loop
while True:
	# clear screen
	screen.fill(bg_color)

	# handle events
	for event in pygame.event.get():

		if event.type == pygame.QUIT:
			pygame.quit() # close pygame
			sys.exit() # exit infinite loop
		# handle mouse clicks
		if event.type == pygame.MOUSEBUTTONDOWN:
			test.state_play = False
			test.mousePressHandler(event.pos)

		if event.type == pygame.MOUSEBUTTONUP:
			test.mouseUpHandler(event.pos)	

		# handle mouse hold and drag -> follows mouse click event
		if event.type == pygame.MOUSEMOTION and pygame.mouse.get_pressed()[0]:
			test.mouseDragHandler(event.pos)

		# handle changing interaction mode by keyboard
		if event.type == pygame.KEYDOWN:
			test.keyPressHandler(event.key)

	test.solve()
	# draw things
	test.drawProspectiveBeam()
	for beam in test.solver.beams:
		test.drawBeam(beam)

	# update the screen
	msElapsed = clock.tick(60) # force to 60 fps
	pygame.display.update() # analagous to swap buffers
