import encoder
import pyagram
import test

code = test.default4
pyagram = pyagram.Pyagram(code, debug=True) # Remove debug=True (it'll default to False) when done.
serialized_pyagram = encoder.PyagramEncoder().encode(pyagram)
