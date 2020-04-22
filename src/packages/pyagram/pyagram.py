import io
import sys

from . import encode
from . import postprocess
from . import preprocess
from . import pyagram_state
from . import trace

class Pyagram:
    """
    """

    def __init__(self, code, *, debug):
        old_stdout = sys.stdout
        new_stdout = io.StringIO()
        try:
            try:
                preprocessor = preprocess.Preprocessor(code)
                preprocessor.preprocess()
            except SyntaxError as exception:
                self.encoding = 'syntax_error'
                self.data = 'TODO' # TODO
            else:
                bindings = {}
                state = pyagram_state.State(
                    encode.Encoder(preprocessor),
                    new_stdout,
                )
                tracer = trace.Tracer(state)
                sys.stdout = new_stdout
                tracer.run(
                    preprocessor.ast,
                    globals=bindings,
                    locals=bindings,
                )
                sys.stdout = old_stdout
                postprocessor = postprocess.Postprocessor(state)
                postprocessor.postprocess()
                self.encoding = 'pyagram'
                self.data = state.snapshots
        except Exception as exception:
            sys.stdout = old_stdout
            if debug:
                print(new_stdout.getvalue())
                raise exception
            self.encoding = 'pyagram_error'
            self.data = 'TODO' # TODO

    def serialize(self):
        """
        """
        return {
            'encoding': self.encoding,
            'data': self.data,
        }
