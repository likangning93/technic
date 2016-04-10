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


def drawBeam(beam):
	pos = beam.position
	end = beam.getPosAlongBeam(beam.length)
	pygame.draw.lines(screen, black, False, [(int(pos.x),int(pos.y)), (int(end.x),int(end.y))], 1)
	pygame.draw.circle(screen, black, (int(pos.x), int(pos.y)), 2, 0)
	pygame.draw.circle(screen, black, (int(end.x), int(end.y)), 2, 0)

def drawJoint(joint):
	pos = joint.position
	pygame.draw.circle(screen, red, (int(pos.x), int(pos.y)), 5, 2)

solver = technicSolver.generateDefaultLinkage()
driverJoint = None
for joint in solver.joints:
	if joint.isDriver:
		driverJoint = joint
		break


time = 1
print
# main drawing loop
while True:
	# handle events
	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			pygame.quit() # close pygame
			sys.exit() # exit infinite loop

	screen.fill(bg_color)

	solver.solve(time)
	time += 1

	# draw things, advance simulation
	for beam in solver.beams:
		drawBeam(beam)

	for joint in solver.joints:
		drawJoint(joint)

	# update linkage driver
	driverJoint.preferredAngle += 0.1


	# update the screen
	msElapsed = clock.tick(60) # force to 60 fps
	pygame.display.update() # analagous to swap buffers
