import parts
from parts import Beam, Joint
import math2d
from math2d import vec2

import pygame
import sys

print("how to use:")
print("-press 'a' to enter joint add mode.")
print("-click on the beam to add joints")
print("-press 's' to enter joint select and manipulate mode")
print("-beam will be oriented by the last two joints selected")
print("-beam will prioritize positioning by the least recently selected")
print("-press 'c' to clear the joint selection")
print("-press 'p' to dump test beam and sim state information")


pygame.init()
clock = pygame.time.Clock() # for maintaining constant update time
screen = pygame.display.set_mode((640,480)) # open a window

# some general drawing members
bg_color = (255, 255, 255)
black = (0,0,0)
red = (255, 0, 0)
blue = (0, 0, 255)
teal = (0, 255, 255)

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


class beamTestState(object):
	def __init__(self):
		# simulation state members
		self.state_staticJoint = None # what stays stationary
		self.state_mobileJoint = None # what gets dragged

		self.state_mode_dragJoint = False # activate by pressing s
		self.state_mode_addJoints = False # activate by pressing a

		self.testBeam = Beam(0);
		self.testBeam.position = vec2(320, 240)
		self.testBeam.length = 100.0

	def mousePressHandler(self, mousePos):
		#print(str(mousePos))
		mousePos_vec2 = vec2(mousePos[0], mousePos[1])

		# "add joint" mode handler
		if self.state_mode_addJoints == True:
			posOnBeam = self.testBeam.onBeam(mousePos_vec2, 5.0)
			if posOnBeam: # not None
				#print(posOnBeam)
				newJoint = Joint()
				newJoint.beam1 = self.testBeam
				newJoint.beam1_pos = posOnBeam * self.testBeam.length
				self.testBeam.joints.append(newJoint)
				self.testBeam.updateAllJoints(0)
		
		# "select and drag" mode handler
		if self.state_mode_dragJoint == True:
			# check if any joint has been clicked. update selection if so
			for joint in self.testBeam.joints:
				if joint.positionOnJoint(mousePos_vec2, 5.0) and joint is not self.state_mobileJoint:
					self.state_staticJoint = self.state_mobileJoint
					self.state_mobileJoint = joint
					break
			for joint in self.testBeam.joints:
				# handle fixing up colors
				joint.color = red
				if joint is self.state_staticJoint:
					joint.color = blue
				elif joint is self.state_mobileJoint:
					joint.color = teal


	def mouseDragHandler(self, mousePos):
		mousePos_vec2 = vec2(mousePos[0], mousePos[1])
		if self.state_mode_dragJoint:
			if self.state_mobileJoint and not self.state_mobileJoint.positionOnJoint(mousePos_vec2, 5.0):
				self.state_mobileJoint.position = mousePos_vec2
				if self.state_staticJoint:
					self.testBeam.snapToJoints(self.state_staticJoint, self.state_mobileJoint)
				else:
					self.testBeam.snapToJoint(self.state_mobileJoint)
				self.testBeam.updateAllJoints(0)

	def keyPressHandler(self, key):
		#print(key)
		if key == 's': # switch to joint select-and-drag mode
			#print('s')
			print("switched to joint select and drag mode")
			self.state_mode_dragJoint = True
			self.state_mode_addJoints = False
		if key == 'a': # switch to joint add mode
			#print('a')
			print("switched to add joint mode")
			self.state_mode_dragJoint = False
			self.state_mode_addJoints = True
		if key == 'p': # print some beam information
			print("requested dump of test beam information")
			print("position and end position:")
			print(self.testBeam.position)
			endPos = self.testBeam.getPosAlongBeam(self.testBeam.length)
			print(endPos)
			print("static joint: " + str(self.state_staticJoint))
			print("mobile joint: " + str(self.state_mobileJoint))

		if key == 'c': # clear selection
			print("requested to clear selection info")
			self.state_staticJoint = None
			self.state_mobileJoint = None
			for joint in self.testBeam.joints:
				# handle fixing up colors
				joint.color = red
				if joint is self.state_staticJoint:
					joint.color = blue
				elif joint is self.state_mobileJoint:
					joint.color = teal			

test = beamTestState()

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
			#print(event)
			test.keyPressHandler(event.unicode)

	screen.fill(bg_color)

	# draw things, advance simulation
	drawBeam(test.testBeam)

	# update the screen
	msElapsed = clock.tick(60) # force to 60 fps
	pygame.display.update() # analagous to swap buffers	