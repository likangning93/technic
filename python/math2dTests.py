import math2d
from math2d import vec2

""" unit tests """

if True:
	print("testing to str and constructors")
	a = vec2(1.0, 2.0)
	print(a)
	b = vec2();
	print(b)
	print("")	

if True:
	print("testing copy")
	a = vec2(1.0, 2.0)
	b = a.copy()
	print("a is initially " + str(a))	
	print("b is initially " + str(b))
	a.x = 2.0
	print("a is now :" + str(a))
	print("b is now :" + str(b))
	print("")	

if True:
	print("testing math addition (__add__)")
	a = vec2(2.0, 2.0)
	b = vec2(1.0, 1.0)
	print(a + b)
	print("")	

if True:
	print("testing math addition (__iadd__)")
	a = vec2(2.0, 2.0)
	b = vec2(1.0, 1.0)
	a += b
	print(a)
	print(b)
	print("")

if True:
	print("testing math subtraction (__sub__)")
	a = vec2(2.0, 2.0)
	b = vec2(1.0, 1.0)
	print(a - b)
	print(b - a)
	print("")	

if True:
	print("testing math subtraction (__isub__)s")
	a = vec2(2.0, 2.0)
	b = vec2(1.0, 1.0)
	a -= b
	print(a)	
	print("")	

if True:
	print("testing math division")
	a = vec2(2.0, 2.0)
	b = 1.5
	print(a / b)
	a /= b
	print(a)
	print("")	

if True:
	print("testing math multiplication")
	a = vec2(2.0, 2.0)
	b = 1.5
	print(a * b)
	a *= b
	print(a)
	print("")

if True:
	print("testing norm and length")
	a = vec2(10.0, -30.01)
	print("a.norm() is " + str(a.norm()))
	print("a.norm().length() is " + str(a.norm().length()))
	print("a is " + str(a))
	print("a.length() is " + str(a.length()))
	print("")

if True:
	print("testing rotation")
	a = vec2(0.0, 10.0)
	b = a.rotate(1.57079632679)
	print("a is " + str(a))
	print("b is a rotated by half pi. b is " + str(b))
	print("")

if True:
	print("testing dot product")
	a = vec2(2.0, 2.0)
	b = vec2(3.0, 3.0)
	print(str(math2d.dot(a, b)))
	print("")

if True:
	print("testing angleToOrientation in Q1")
	a = vec2(10.0, 10.0)
	print(str(math2d.angleToOrientation(a)))
	print("")

if True:
	print("testing angleToOrientation in Q2")
	a = vec2(-10.0, 10.0)
	print(str(math2d.angleToOrientation(a)))
	print("")	

if True:
	print("testing angleToOrientation in Q3")
	a = vec2(-10.0, -10.0)
	print(str(math2d.angleToOrientation(a)))
	print("")	

if True:
	print("testing angleToOrientation in Q4")
	a = vec2(10.0, -10.0)
	print(str(math2d.angleToOrientation(a)))
	print("")	

if True:
	print("testing vectorAlongDirection")
	a = math2d.vectorAlongDirection(0.78539816339)
	print(a)
	print("")