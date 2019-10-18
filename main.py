import pyagram
import test

# TODO: Wrap everything in a try-except-then clause.
code = test.testnested
pyagram = pyagram.Pyagram(code, debug=True)
serialized_pyagram = pyagram.serialize()
