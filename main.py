import pyagram
import test

# TODO: Wrap everything in a try-except-then clause.
code = test.testnested
pyagram = pyagram.Pyagram(code, debug=False)
serial_pyagram = pyagram.serialize()
