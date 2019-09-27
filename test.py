testnested = """
def f(x, h = None):
    a = 1
    return x
def g(y):
    b = 2
    return y + 1
def h(q):
    return q - 1
f(g(2), h(3))
f(h(g(2)))
"""

starargs1 = """
def g(a, b, c, d, *e):
    return None

l1 = [1, 2]
l2 = [3, 4, 5, 6]
x = g(*l1, *l2)
"""

return_none = """
def f():
    return

x = f()
"""

# test instantiation like `a = type(b)(c, d)`

default1 = """
def f(x=4):
    return x

a = f()
b = f(5)
"""

default2 = """
z = 100

def g():
    return z

def f(x=g()):
    return x

a = f()
z = 50
b = f()
"""

default3 = """
a = 100

def g():
    return [4]

def h():
    return a

def f(x, y=g() + [5, 6], z=h()):
    return x + y[0] + z

b = f(6, [14]) # We should see [4, 5, 6] in memory at this point!
c = f(6)
a = 0
d = f(16)
"""

default4 = """
a = [1, 2, 3]

def f(x=a, y=[4, 5, 6]):
    return x[-1]

y = f()
a.append(4)
z = f()
"""

kwargs1 = """
def f(x, y):
    return x + y

def x():
    print('x')
    return 1

def y():
    print('y')
    return 2

f(x(), y()) # Should see x y 3
f(y=y(), x=x()) # Should see y x 3
"""

rebind_params = """
def f(x, y):
    x = x + 10
    y = 100
    return x + y + z

z = 100
a = f(90, 5)
"""

rebind_param_pointers = """
def f(x, y):
    x.append(4)
    y = y()
    x = x[-2]
    y = 100
    return x[0] + y

a = [1, lambda: 2, [3]]
b = f(a, a[1])
"""

return_mutative = """
def f():
    return 5

x = 4
x = f()
"""

plain = """
def f(x):
    return x

a = f(4)
"""

nested_append = """
a = []
a.append(a.append(1))
"""

hidden_flags0 = """
def f():
    return 0

a = []
a.extend([a.append(1), f()])
"""

hidden_flags1 = """
def f(*args):
    return args[0]

a = []
a.extend([a.append(1), f(2), f(3), f(a.append([4, f(5)]))])
b = f(6)
a.append(6)
"""

lambda1 = """
x = (lambda x, y: x + y)(3, 4)
x = (lambda x, y: x + y)((lambda: 3)(), (lambda z: z ** 2)(2)) + 1
"""

lambda_arg1 = """
def f():
    def g(h):
        return h()
    return g(lambda: 4)
g = f()
"""

lambda_arg2 = """
def f(g):
    return g(lambda: 4)
def g(h):
    return h()
x = f(g)
"""

lambda_arg3 = """
def f(funcs):
    total = 0
    for func in funcs:
        total += func(total)
    return total

def g():
    return f([lambda x: 1, lambda x: 2, lambda x: x])

x = g()
"""

lineno1 = """
def f():
    return 3

def g(a, b):
    return a + b

a = g(f(), g(1, 2))
""" # After f() returns, but before g(1, 2), the lineno should go back to 8.

simultaneous_identical_code_objs = """
def f(x=None):
    return lambda: x

def g(a, b):
    return None

a = g(f(), f(f()))
"""

simultaneous2 = """
def f():
    x = 4
    g, h = (lambda: x), (lambda: x)
    return g, h

g, h = f()
a = g()
b = h()
"""

identical_code_objs2 = """
def f():
    return lambda: 0

a = f() and f()
b = f()() and f()()
"""

global_lookup = """
x = 1
def f():
    return x

def g():
    return f()

a = f()
b = g()
"""

parent_lookup1 = """
def f():
    x = 1
    def g():
        return x
    return g

g = f()
x = g()
"""

parent_lookup2 = """
def f(x):
    def g():
        return x
    return g

g = f(4)
x = g()
"""

ret_lambda = """
def f(x):
    return (lambda: x)()
def g(x):
    def h(y):
        return x + y()
    return h(lambda: 5)
a = f(4)
b = g(3)
"""

curry1 = """
x = (lambda x: lambda y: lambda z: x + y + (lambda x: x + z)(y))(1)(2)(3)
"""

test_two_funcs = """
f = lambda x: x + 1
g = lambda x: x - 1
h = lambda x, y: x + y
x = h(f(4), g(4))
"""

test_mut = """
a = [1, 2, 3]
a.append(4)
b = a
b = 5
"""

nested_lists = """
a = [1, 2, 3]
b = [4, 5, 6]
a.append(b)
c = a
d = c + b
e = d
"""

# test a function in a list
# also test a lambda in a list, like [1, 2, lambda x: x]

nested_2 = """
a = [1, 2, 3, [4, 5, 6]]
b = a[0]
c = a[1]
d = a[2]
e = a[3]
"""

cyclic_lists = """
a = [1, 2, 3]
b = [a, 4, 5]
a.append(b)
"""

test_same_code_obj = """
def f():
    def g():
        return
    return g

g1 = f()
g2 = f()

g1()
g2()
""" # g1's frame and g2's frame should show that they were opened by different functions, even though said functions share the same code object

# See if it tracks __init__, __str__, and __repr__. Try it for when the user defines each of these magic methods, as well as for when the user does not.
test_init1 = """
class A:
    a = 10

a = A()
"""
test_init2 = """
class A:
    a = 10
    def __init__(self, x):
        self.x = x

a = A(4)
"""
test_str1 = """
class A:
    a = 10

a = A()
b = str(a)
"""
test_str2 = """
class A:
    a = 10
    def __str__(self):
        return f'object A [a={self.a}]'

a = A()
b = str(a)
"""
test_str_extra = """
class A:
    a = 10

x = (lambda x: x)(4)
a = A()
b = str(a)
"""

# Test various implicit function calls. (Are magic methods the only functions that called implicitly? What about `@property` tags? What about when `__str__` implicitly calls `__repr__`? What about default arguments, they happen implicitly as soon as you define the function right?)
# Also make sure it continues working smoothly AFTER the implicit function call has been handled; there's a concern that it can handle the implicit call OK but then messes up.

immediate_error = '1 / 0'

immediate_lambda = '(lambda: 4)()'

immediate_call_1 = 'max(1, 2)'
immediate_call_2 = '1 + 2'
immediate_call_3 = 'int()'

immediate_print = 'print("hello world")'

return_call = """
def f(x):
    return g(x)
def g(x):
    return x
y = f(4)
"""

testsrc = """
def f(x):
    return x
z = f(f)(f(3))
"""

testrebind = """
def f(x):
    x += 1
    y = 3
    y = 4
    return x + y

z = f(10)
"""

testrepr = """
class C():
    def __repr__(self):
        x = 1
        def f():
            x = 2
            return x
        a = f()
        return "hi"
c = C()
print(c)
"""

testobject = """
class Dog():
    numdogs = 0
    def __init__(self, height):
        self.height = height
        Dog.numdogs += 1
bigdog = Dog(100)
smalldog = Dog(5)
"""

testrecursion = """
def f(x):
    if (x < 0):
        return 'hi'
    print(x)
    a = f(x - 1)
    return a
f(3)
"""

framechange = """
a = 2
def f():
    a = 1
    return 1
a = f()
"""

multframes = """
def f():
    def g(a):
        b = lambda : a
        return b
    q = g(1)
    w = g(2)
f()
"""

frame = """
a = 1
def f():
    a = 3
    b = 2
    def g():
        a = 2
        return a
    q = g()
    return b
c = f()
"""

test2 = """
def f():
    a = 1
    b = 2
    c = "3"
    d = lambda x: x
    f = print("hi")
    g = [1, d, 3]
    print(locals())

f()
"""


test3 = """
def g(y):
    b = 2
    return y + 1
def h(q):
    return q - 1
g(h(7))
"""

testnonlocal = """
def f():
    x = 3
    def g():
        nonlocal x
        x = 'a'
    g()
f()
"""

testglobal = """
x = 'a'
def f():
    global x
    x = 3
f()
"""

testlstcomp = """
x = [x for x in range(10) if x % 2 == 0]
"""

testlambda = """
def f():
    x = lambda y, q: y(1)
    return x(lambda q: q * 10, lambda q: q * 10)
f()
"""

funcparent = """
x = 1
def f():
    x = 3
    def g():
        return x
    return g
y = f()()
"""

# See old CS 61A exams.
