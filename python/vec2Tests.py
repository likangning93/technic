from vec2 import vec2

""" unit tests """

if True:
	print("testing to str and constructors")
	a = vec2(1.0, 2.0)
	print(a)
	b = vec2();
	print(b)

if True:
	print("testing copy")
	a = vec2(1.0, 2.0)
	b = a.copy()
	print("a is initially " + str(a))	
	print("b is initially " + str(b))
	a.x = 2.0
	print("a is now :" + str(a))
	print("b is now :" + str(b))

if True:
	print("testing math addition")
	a = vec2(2.0, 2.0)
	b = vec2(1.0, 1.0)
	print(a + b)
	a += b
	print(a)

if True:
	print("testing math subtraction")
	a = vec2(2.0, 2.0)
	b = vec2(1.0, 1.0)
	print(a - b)
	a -= b
	print(a)

if True:
	print("testing math division")
	a = vec2(2.0, 2.0)
	b = 1.5
	print(a / b)
	a /= b
	print(a)

if True:
	print("testing math multiplication")
	a = vec2(2.0, 2.0)
	b = 1.5
	print(a * b)
	a *= b
	print(a)
