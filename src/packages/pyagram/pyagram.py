import io
import sys

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
                    preprocessor.summary,
                    new_stdout,
                )
                tracer = trace.Tracer(state)
                sys.stdout = new_stdout
                try:
                    tracer.run(
                        preprocessor.ast,
                        globals=bindings,
                        locals=bindings,
                    )
                except Exception as exception:
                    assert state.program_state.curr_element is state.program_state.global_frame
                    has_uncaught_exception = True
                else:
                    has_uncaught_exception = False
                print(has_uncaught_exception) # TODO: Give this to the postprocessor?
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
