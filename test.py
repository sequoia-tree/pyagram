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

#
