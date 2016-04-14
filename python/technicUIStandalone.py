import pygame
import sys
import technicSolver

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


def drawBeam(beam):
	pos = beam.position
	end = beam.getPosAlongBeam(beam.length)
	pygame.draw.lines(screen, black, False, [(int(pos.x),int(pos.y)), (int(end.x),int(end.y))], 1)
	pygame.draw.circle(screen, black, (int(pos.x), int(pos.y)), 2, 0)
	pygame.draw.circle(screen, black, (int(end.x), int(end.y)), 2, 0)
	# draw each of the joints along this beam
	for joint in beam.joints:
		pos = joint.positionRelative(beam)
		pygame.draw.circle(screen, joint.color, (int(pos.x), int(pos.y)), 6, 1)
		pygame.draw.circle(screen, joint.color, (int(pos.x), int(pos.y)), 2, 1)

def drawJoint(joint):
	pos = joint.position
	pygame.draw.circle(screen, red, (int(pos.x), int(pos.y)), 5, 2)

class solverTestState(object):
	def __init__(self):
		# simulation state members
		self.state_mode_dragManip = False # activate by pressing d
		self.state_mode_addBeams = False # activate by pressing b
		self.state_mode_addJoints = False # activate by pressing j
		self.state_play = False

		self.state_mouseDownCoord = None

		self.state_selectedBeam = None
		self.state_onlyStaticJoint = None

		self.time = 0
		self.solver = technicSolver.generateDefaultLinkage()
		# get the driver joint, we need that.
		self.driverJoint = None
		for joint in self.solver.joints:
			if joint.isDriver:
				self.driverJoint = joint
				break

	def solve(self):
		if self.state_play:
			self.driverJoint.preferredAngle += 2.0
			self.time += 1			
			self.solver.solve(self.time)

	def stepFwd(self):
		self.driverJoint.preferredAngle += 2.0
		self.time += 1		
		self.solver.solve(self.time)

	def stepBck(self):
		self.driverJoint.preferredAngle -= 2.0
		self.time -= 1
		self.solver.solve(self.time)

	def getClickedBeams(self, pos_vec2):
		return [beam for beam in self.solver.beams if beam.onBeam(pos_vec2, clickDist)]

	def getClickedJoints(self, pos_vec2):
		return [joint for joint in self.solver.joint if joint.positionOnJoint(pos_vec2, clickDist)]

	def addBeam(self, beam):
		self.solver.beams.append(beam)

	def deleteBeam(self, beam):
		if beam not in self.solver.beams:
			return
		self.solver.beams.remove(beam)
		# delete all joints linked to this beam
		for joint in beam.joints:
			self.solver.joints.remove(joint)
			joint.delink

	def addJointsOnBeams(self, pos_vec2):
		clickedBeams = self.getClickedBeams(self, pos_vec2)
		# generate a new joint between every pair of clicked beams
		numClicked = len(clickedBeams)
		for i in xrange(numClicked - 1):
			newJ = clickedBeams[i].joinByWorldPos(clickedBeams[i + 1], pos_vec2, clickDist)
			self.solver.joints.append(newJ)

	def deleteJoint(self, joint):
		joint.delink
		self.solver.joints.remove(joint)

	def mousePressHandler(self, mousePos):
		pass

	def mouseDragHandler(self, mousePos):
		pass

	def keyPressHandler(self, key):
		#print(key)
		if key == pygame.K_s:
			print("changed to select and drag mode")

		if key == pygame.K_a:
			print("changed to beam adding mode")

		if key == pygame.K_j:
			print("changed to joint adding mode")

		if key == pygame.K_RIGHT:
			print("ffwd")

		if key == pygame.K_LEFT:
			print("back")

		if key == pygame.K_SPACE:
			print("toggle pause/play")

		pass

test = solverTestState()

# main drawing loop
while True:
	# handle events
	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			pygame.quit() # close pygame
			sys.exit() # exit infinite loop
		# handle mouse interaction
		if event.type == pygame.MOUSEBUTTONDOWN:
			test.mousePressHandler(event.pos)

		if event.type == pygame.MOUSEMOTION and pygame.mouse.get_pressed()[0]:
			test.mouseDragHandler(event.pos)

		# handle changing interaction mode by keyboard
		if event.type == pygame.KEYDOWN:
			test.keyPressHandler(event.key)



	screen.fill(bg_color)

	# update the screen
	msElapsed = clock.tick(60) # force to 60 fps
	pygame.display.update() # analagous to swap buffers
