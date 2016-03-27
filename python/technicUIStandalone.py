import pygame
import sys
#import technicSolver

# help from https://www.cs.ucsb.edu/~pconrad/cs5nm/topics/pygame/drawing/

pygame.init()
clock = pygame.time.Clock() # for maintaining constant update time
screen = pygame.display.set_mode((800,600)) # open a window

bg_color = (255, 255, 255)
black = (0,0,0)

pos = 100

# main drawing loop
while True:
	# handle events
	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			pygame.quit() # close pygame
			sys.exit() # exit infinite loop

	screen.fill(bg_color)

	# draw things, advance simulation
	pygame.draw.lines(screen, black, False, [(pos,100), (150,200), (200,100)], 1)
	pos += 1

	msElapsed = clock.tick(60) # force to 60 fps
	pygame.display.update() # analagous to swap buffers