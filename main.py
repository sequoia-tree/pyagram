import wrap
import pyagram

import test

src_code = test.immediate_lambda
new_code = wrap.wrap_calls(src_code)
pyagram = pyagram.Pyagram(new_code)
