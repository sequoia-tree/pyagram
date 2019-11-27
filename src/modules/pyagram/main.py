from . import pyagram
from . import test

# TODO: Wrap everything in a try-except-then clause.
code = test.testnested
pyagram = pyagram.Pyagram(code, debug=True)
serialized_pyagram = pyagram.serialize()

# TODO: Rename this `test.py`? Then in /app.py you can import pyagram.py and do the above code but with debug=False.
