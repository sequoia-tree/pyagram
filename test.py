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

test_two_funcs = """
f = lambda x: x + 1
g = lambda x: x - 1
h = lambda x, y: x + y
x = h(f(4), g(4))
"""

# See if it tracks __init__, __str__, and __repr__.
test_init1 = """
class A:
    a = 10

a = A()
"""
test_init2 = """
class A:
    def __init__(self, x):
        self.x = x
    a = 10

a = A(4)
"""
test_str = """
class A:
    a = 10

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
