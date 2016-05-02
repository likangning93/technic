import json
import technicSolver
from parts import Joint, Beam
from math2d import vec2

# json markers
TYPE = 'TYPE'
JOINT = str(Joint)
BEAM = str(Beam)
NAME = 'NAME'

POS = 'POS'
ANGLE = 'ANGLE'
DRIVE = 'DRIVE'
PRISM = 'PRISM'
ROOT = 'ROOT'
LENGTH = 'LENGTH'
ROTAT = "ROTAT"
JOINTS = 'JOINTS'
BEAMS = 'BEAMS'
ID = 'ID'

def export(solver, filename):
	"""
	1) Build dictionaries of items to names
	2) Put all the items in the linkage into JSON format dictionaries
	3) Form this into a giant list, then dump it out to filename.

	Beam:
		Type 		(String)
		Name 		(String)
		isRoot 		(Boolean)
		Position 	(Float Float)
		Length 		(Float)
		Joints 		(String List)

	Joint:
		Type 		(String)
		Name 		(String)
		Beams		(String, String)
		Positions	(Float, Float)
		isDriven	(Boolean)
		Angle		(float)
	"""
	# build dictionaries of items to names
	joint_names = {}
	beam_names = {}
	i = 0
	for joint in solver.joints:
		joint_names[joint] = 'joint' + str(i)
		i += 1

	i = 0
	for beam in solver.beams:
		beam_names[beam] = 'beam' + str(i)
		i += 1

	# put all the items in the linkage into json format dictionaries in a list
	joint_dicts = []
	for joint in solver.joints:
		joint_dict = {}
		joint_dict[TYPE] = JOINT
		joint_dict[NAME] = joint_names[joint]
		joint_dict[BEAMS] = [beam_names[joint.beam1], beam_names[joint.beam2]]		
		joint_dict[POS] = [joint.beam1_pos, joint.beam2_pos]
		joint_dict[DRIVE] = joint.isDriver
		joint_dict[ANGLE] = joint.preferredAngle
		joint_dict[PRISM] = joint.isPrismatic
		joint_dicts.append(joint_dict)

	beam_dicts = []
	for beam in solver.beams:
		beam_dict = {}
		beam_dict[TYPE] = BEAM
		beam_dict[NAME] = beam_names[beam]
		beam_dict[ROOT] = (beam is solver.root)
		beam_dict[POS] = [beam.position.x, beam.position.y]
		beam_dict[LENGTH] = beam.length
		beam_dict[ROTAT] = beam.rotation
		beam_dict[JOINTS] = [joint_names[joint] for joint in beam.joints]
		beam_dict[ID] = beam.id
		beam_dicts.append(beam_dict)

	# export to file
	json_dict = {"JOINTS" : joint_dicts, "BEAMS" : beam_dicts}
	json_str = json.dumps(json_dict, indent=4, separators=(',', ': '))
	json_file = open(filename, 'w')
	json_file.write(json_str)
	json_file.close()

def load(filename):
	"""
	1) read the json
	2) make all the beams. build dictionary of beams to beam names.
		-make a new solver
		-update it as we go
	3) walk over the joint list and do the connections
		-update the solver as we go

	"""
	# read the json
	json_file = open(filename, 'r')
	json_dict = json.loads(json_file.read())
	json_file.close()
	beam_dicts = json_dict["BEAMS"]
	joint_dicts = json_dict["JOINTS"]

	solver = technicSolver.Solver()

	# make all the beams. build a dictionary of beams to beam names/joint lists
	names_beams = {}
	names_jointNames = {}

	for beam_dict in beam_dicts:
		beam = Beam(beam_dict[ID])
		beam.length = beam_dict[LENGTH]
		beam.position = vec2(beam_dict[POS][0], beam_dict[POS][1])
		beam.rotation = beam_dict[ROTAT]
		if beam_dict[ROOT]:
			solver.root = beam
		solver.beams.append(beam)
		names_beams[beam_dict[NAME]] = beam
		names_jointNames[beam_dict[NAME]] = beam_dict[JOINTS]

	# walk over the list of joints and build connections
	for joint_dict in joint_dicts:
		beam1 = names_beams[joint_dict[BEAMS][0]]
		beam2 = names_beams[joint_dict[BEAMS][1]]
		pos1 = joint_dict[POS][0]
		pos2 = joint_dict[POS][1]
		joint = beam1.joinWithBeam(pos1, beam2, pos2)
		joint.isDriver = joint_dict[DRIVE]
		joint.preferredAngle = joint_dict[ANGLE]
		if PRISM in joint_dict:
			joint.isPrismatic = joint_dict[PRISM]
		solver.joints.append(joint)

	return solver
