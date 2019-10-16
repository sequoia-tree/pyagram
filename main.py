import encoder
import pyagram
import test

# TODO: Wrap everything in a try-except-then clause.
code = test.testnested
pyagram = pyagram.Pyagram(code, debug=True) # Remove debug=True (it'll default to False) when done.
serialized_pyagram = encoder.PyagramEncoder().encode(pyagram)
