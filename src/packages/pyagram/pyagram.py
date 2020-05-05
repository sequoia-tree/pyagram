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


                    # TODO: I think that if an exception is caught, then we're chilling. But if there's an uncaught one, the next step will be a return from <module>?
                    # TODO: If it's an uncaught exception, the trace should stop then, or perhaps the next step, right? Whereas if it's caught, the trace will keep going for a while?

                    # TODO: Start by making it work for errors that get caught.

                    # TODO: Actually, when you get to uncaught errors, I don't think you'll need this try/except block. You can detect the exception as you already do, perhaps just modify the `if traceback.tb_next is None` block in state.py?

                    raise exception # TODO: Delete this and do something else.


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
