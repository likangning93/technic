import pygame
import sys
import technicSolver

# help from https://www.cs.ucsb.edu/~pconrad/cs5nm/topics/pygame/drawing/

def drawBeam(beam):
	pos = beam.position
	end = beam.getPosAlongBeam(beam.length)
	pygame.draw.lines(screen, black, False, [(pos.x,pos.y), (end.x,end.y)], 1)

pygame.init()
clock = pygame.time.Clock() # for maintaining constant update time
screen = pygame.display.set_mode((640,480)) # open a window

bg_color = (255, 255, 255)
black = (0,0,0)

solver = technicSolver.generateDefaultLinkage()

# main drawing loop
while True:
	# handle events
	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			pygame.quit() # close pygame
			sys.exit() # exit infinite loop

	screen.fill(bg_color)

	# draw things, advance simulation
	for beam in solver.beams:
		drawBeam(beam)

	# update the screen
	msElapsed = clock.tick(60) # force to 60 fps
	pygame.display.update() # analagous to swap buffers
