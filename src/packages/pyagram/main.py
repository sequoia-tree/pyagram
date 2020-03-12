from . import pyagram
from . import test

code = test.testnested
pyagram = pyagram.Pyagram(code, debug=True)
serialized_pyagram = pyagram.serialize()

# TODO: Move this into `test.py`? You don't actually need this file anymore (except for testing) bc app.py imports a different one.
