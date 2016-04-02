import technicSolver


solver = technicSolver.generateDefaultLinkage();

if True:
	print("testing beam-level quad yielding")
	for quad in solver.root.yieldQuad():
		print(str(len(quad)))
		print(str(quad[0]))
		print(str(quad[1]))
		print(str(quad[2]))
		print(str(quad[3]))
	print("done testing beam-level quad yielding")
	print(" ")
