import pygame
import sys
import technicSolver
from parts import Beam, Joint
import math2d
from math2d import vec2
import linkageImportExport
import datetime

# help from https://www.cs.ucsb.edu/~pconrad/cs5nm/topics/pygame/drawing/

# pygame stuff
pygame.init()
pygame.display.set_caption('technic standalone UI')
clock = pygame.time.Clock() # for maintaining constant update time
screen = pygame.display.set_mode((800,600)) # open a window
basicfont = pygame.font.SysFont(None, 14)

# drawing constants
bg_color = (255, 255, 255)
black = (0,0,0)
red = (255, 0, 0)
blue = (0, 0, 255)
teal = (0, 255, 255)
green = (0, 200, 0)

# simulator/UI constants
clickDist = 5.0
outputFail = False

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

		if self.state_show_labels: # toggled with l
			# draw text of name
			text = basicfont.render("beam " + str(beam.id), True, (255, 0, 0), (255, 255, 255))
			pos_text = beam.getPosAlongBeam(beam.length / 2.0)
			screen.blit(text, (pos_text.x, pos_text.y))

		# draw each of the joints along this beam
		for joint in beam.joints:
			self.drawJoint(joint, beam)

	def drawJoint(self, joint, beam):
		if joint.isPrismatic:
			pos1 = joint.positionRelative(beam)
			pos2 = joint.positionRelative(joint.getOtherbeam(beam))
			clr = green
			if joint == self.state_selectedJoint:
				clr = blue
			pygame.draw.circle(screen, clr, (int(pos1.x), int(pos1.y)), 6, 1)	
			pygame.draw.lines(screen, clr, False, [(int(pos1.x),int(pos1.y)), (int(pos2.x),int(pos2.y))], 3)

		else:
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


	def __init__(self, filename=None):
		# simulation state members
		self.state_mode_dragManip = False # activate by pressing d
		self.state_mode_addBeams = False # activate by pressing b
		self.state_mode_addRotationJoints = False # activate by pressing j
		self.state_mode_addPrismaticJoints = False # activate by pressing p		
		self.state_mode_addGears = False # activate by pressing g		

		self.state_play = False
		self.state_show_labels = False # toggled with l

		self.state_mouseDownCoord = None
		self.state_mouseLastCoord = None

		self.state_selectedBeam = None
		self.state_selectedJoint = None
		self.state_soleStaticJoint = None
		self.nextBeamID = 5

		self.dAngle = 0.1

		self.time = 1
		self.solver = technicSolver.generateDefaultLinkage()
		if filename is not None:
			self.solver = linkageImportExport.load(filename)
		# get the driver joint, we need that.
		self.driverJoint = None
		for joint in self.solver.joints:
			if joint.isDriver:
				self.driverJoint = joint
				break

	def solve(self):
		if self.state_play:
			if not outputFail:
				noDeadlock = self.solver.solve(self.time)
				if not noDeadlock:
					self.dAngle = -self.dAngle
				self.driverJoint.preferredAngle += self.dAngle
				self.time += 1
			else:
				try:
					noDeadlock = self.solver.solve(self.time)
					if not noDeadlock:
						self.dAngle = -self.dAngle
					self.driverJoint.preferredAngle += self.dAngle
					self.time += 1
				except TypeError:
					print("type error encountered!")
					print("possible that you are missing a quad?")
					filename = datetime.datetime.now().isoformat()
					filename += " type error fail.json"
					save_or_no = raw_input("Save log file? y/n")
					if save_or_no == 'y':
						linkageImportExport.export(self.solver, filename)
					quit()
				except AttributeError:
					print("attribute error encountered!")
					print("possible that a quad is unsolveable?")
					filename = datetime.datetime.now().isoformat()
					filename += " attrib error fail.json"
					save_or_no = raw_input("Save log file? y/n")
					if save_or_no == 'y':
						linkageImportExport.export(self.solver, filename)
					quit()

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
		return [joint for joint in self.solver.joints if joint.positionOnJoint(pos_vec2, clickDist)]

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

	def addJointsOnBeams(self, pos_vec2, prismatic):
		clickedBeams = self.getClickedBeams(pos_vec2)
		# generate a new joint between every pair of clicked beams
		numClicked = len(clickedBeams)
		for i in xrange(numClicked - 1):
			newJ = clickedBeams[i].joinByWorldPos(clickedBeams[i + 1], pos_vec2, clickDist)
			if newJ:
				self.solver.joints.append(newJ)
			newJ.isPrismatic = prismatic

	def deleteJoint(self, joint):
		joint.delink()
		self.solver.joints.remove(joint)		

	def mousePressHandler(self, mousePos):
		mousePos_vec2 = vec2(mousePos[0], mousePos[1])
		self.state_mouseDownCoord = mousePos_vec2

		if self.state_mode_dragManip:
			self.selectItem(mousePos_vec2)

		if self.state_mode_addBeams:
			return

		if self.state_mode_addRotationJoints:
			# see if can add joints connecting multiple beams
			self.addJointsOnBeams(mousePos_vec2, False)
			return

		if self.state_mode_addPrismaticJoints:
			# see if can add joints connecting multiple beams
			self.addJointsOnBeams(mousePos_vec2, True)
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

	def selectItem(self, mousePos):
		# set the first one of each as selected
		beams = self.getClickedBeams(mousePos)
		joints = self.getClickedJoints(mousePos)
		# unselect all if you're clicking nowhere
		if len(beams) == 0 and len(joints) == 0:
			self.state_selectedBeam = None
			self.state_selectedJoint = None
			return

		# if you've clicked something selected, deselect that
		# otherwise, set the selection
		if len(beams) > 0:
			if self.state_selectedBeam is beams[0]:
				self.state_selectedBeam = None
			else:
				self.state_selectedBeam = beams[0]

		if len(joints) > 0:
			if self.state_selectedJoint is joints[0]:
				self.state_selectedJoint = None
			else:
				self.state_selectedJoint = joints[0]

	def resetModeState(self):
		self.state_mode_dragManip = False # activate by pressing d
		self.state_mode_addBeams = False # activate by pressing b
		self.state_mode_addRotationJoints = False # activate by pressing j	
		self.state_mode_addPrismaticJoints = False # activate by pressing p
		self.state_mode_addGears = False # activated by pressing g

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

		if key == pygame.K_l:
			print("toggled labels")
			self.state_show_labels = not self.state_show_labels # activate by pressing l

		if key == pygame.K_s:
			print("changed to select and drag mode")
			self.resetModeState()
			self.state_mode_dragManip = True # activate by pressing d

		if key == pygame.K_b:
			print("changed to beam adding mode")
			self.resetModeState()			
			self.state_mode_addBeams = True # activate by pressing b

		if key == pygame.K_j:
			print("changed to rotational joint adding mode")
			self.resetModeState()
			self.state_mode_addRotationJoints = True # activate by pressing j	

		if key == pygame.K_p:
			print("changed to prismatic joint adding mode")
			self.resetModeState()
			self.state_mode_addGears = True # activate by pressing p

		if key == pygame.K_g:
			print("changed to gear adding mode")
			self.resetModeState()
			self.state_mode_addPrismaticJoints = True # activate by pressing g

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

test = solverTestState("deadlock_case1.json")
#test = solverTestState("deadlock_case2.json")
#test = solverTestState()


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
	text = basicfont.render('Hello World!', True, (255, 0, 0), (255, 255, 255))
	pygame.display.update() # analagous to swap buffers
