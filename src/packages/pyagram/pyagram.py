import traceback

from . import encode
from . import postprocess
from . import preprocess
from . import trace
from . import user_exception

class Pyagram:
    """
    A diagram describing the step-by-step execution of a snippet of Python code.

    After initialization, :self.snapshots: is a list of serializable snapshots. Each such snapshot
    encodes the state of the pyagram at a particular step during the execution of the input code.

    :param code: The snippet of Python code for which to create the pyagram.
    :param debug: Whether or not to enable debugging features such as on-the-fly printing of the pyagram during its construction.
    """

    def __init__(self, code, *, debug):
        try:
            try:
                num_lines, global_bindings = len(code.split('\n')), {} # TODO: Isn't the default behavior the same as not specifying the global_bindings?
                preprocessor = preprocess.Preprocessor(code, num_lines)
                preprocessor.preprocess()
                encoder = encode.Encoder(num_lines)
                tracer = trace.Tracer(encoder)
                tracer.run(
                    preprocessor.code,
                    globals=global_bindings,
                    locals=global_bindings,
                )
                postprocessor = postprocess.Postprocessor(tracer.state)
                postprocessor.postprocess()
            except SyntaxError as e:
                self.data = {
                    'lineno': e.lineno,
                    'position': e.offset,
                    'text': e.text,
                }
                self.encoding = 'syntax_error'
            except user_exception.UserException as e:
                self.data = {
                    'type': e.type.__name__,
                    'value': str(e.value),
                    'lineno': e.traceback.tb_lineno,
                }
                self.encoding = 'user_error'
            else:
                self.data = tracer.state.snapshots
                self.encoding = 'pyagram'
        except Exception as e:
            self.data = str(e)
            self.encoding = 'pyagram_error'
            if debug:
                raise e

    def serialize(self):
        """
        """
        return {
            'data': self.data,
            'encoding': self.encoding, # TODO: You have to handle all the following encodings: 'syntax_error' (the student has a syntax error and their code cannot compile), 'pyagram_error' (something went wrong with YOUR code, not the students'), and 'pyagram' (everything went smoothly).
        }
