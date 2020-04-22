import io # TODO: Delete.
import sys # TODO: Delete.

from . import encode
from . import postprocess
from . import preprocess
from . import trace

class Pyagram:
    """
    """

    def __init__(self, code, *, debug):
        old_stdout = sys.stdout # TODO: Change stdout in trace.py.
        new_stdout = io.StringIO() # TODO: Change stdout in trace.py.
        try:
            try:
                preprocessor = preprocess.Preprocessor(code)
                preprocessor.preprocess()
            except SyntaxError as exception:
                self.encoding = 'syntax_error'
                self.data = 'TODO' # TODO
            else:
                bindings = {}
                encoder = encode.Encoder(preprocessor)
                tracer = trace.Tracer(encoder, new_stdout)
                sys.stdout = new_stdout # TODO: Change stdout in trace.py.
                tracer.run(
                    preprocessor.ast,
                    globals=bindings,
                    locals=bindings,
                )
                sys.stdout = old_stdout # TODO: Change stdout in trace.py.
                postprocessor = postprocess.Postprocessor(tracer.state)
                postprocessor.postprocess()
                self.encoding = 'pyagram'
                self.data = tracer.state.snapshots
        except Exception as exception:
            self.encoding = 'pyagram_error'
            self.data = 'TODO' # TODO
        sys.stdout = old_stdout # TODO: Change stdout in trace.py.

    def serialize(self):
        """
        """
        return {
            'encoding': self.encoding,
            'data': self.data,
        }
