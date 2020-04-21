import io
import sys
import traceback

from . import encode
from . import exception
from . import postprocess
from . import preprocess
from . import trace

class Pyagram:
    """
    A diagram describing the step-by-step execution of a snippet of Python code.

    After initialization, :self.snapshots: is a list of serializable snapshots. Each such snapshot
    encodes the state of the pyagram at a particular step during the execution of the input code.

    :param code: The snippet of Python code for which to create the pyagram.
    :param debug: Whether or not to enable debugging features such as on-the-fly printing of the pyagram during its construction.
    """

    def __init__(self, code, *, debug):
        old_stdout = sys.stdout
        new_stdout = io.StringIO()
        sys.stdout = new_stdout
        try:
            num_lines, global_bindings = len(code.split('\n')), {} # TODO: Isn't the default behavior of Bdb.run the same as not specifying the global_bindings?
            try:
                preprocessor = preprocess.Preprocessor(code, num_lines)
                preprocessor.preprocess()
            except SyntaxError as e:
                self.data = {
                    'lineno': e.lineno,
                    'position': e.offset,
                    'text': e.text,
                }
                self.encoding = 'syntax_error'
            else:
                encoder = encode.Encoder(num_lines, preprocessor.lambdas_by_line)
                tracer = trace.Tracer(encoder, new_stdout)
                try:
                    tracer.run(
                        preprocessor.ast,
                        globals=global_bindings,
                        locals=global_bindings,
                    )
                except exception.UserException as e:
                    tracer.state.program_state.exception_snapshot = {
                        'type': e.type.__name__,
                        'value': str(e.value),
                        'lineno': e.traceback.tb_lineno,
                    }
                else:
                    tracer.state.program_state.exception_snapshot = None
                postprocessor = postprocess.Postprocessor(tracer.state)
                postprocessor.postprocess()
                self.data = {
                    'snapshots': tracer.state.snapshots,
                    'exception': tracer.state.program_state.exception_snapshot,
                }
                self.encoding = 'pyagram'
        except Exception as e:
            self.data = str(e)
            self.encoding = 'pyagram_error'
            if debug:
                sys.stdout = old_stdout
                print(new_stdout.getvalue())
                raise e
        sys.stdout = old_stdout

    def serialize(self):
        """
        """
        return {
            'data': self.data,
            'encoding': self.encoding,
        }
