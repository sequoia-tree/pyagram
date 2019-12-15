from . import encode
from . import postprocess
from . import preprocess
from . import pyagram_error
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
        try:
            global_bindings = {} # TODO: Isn't the default behavior the same as not specifying this?
            preprocessor = preprocess.Preprocessor(code)
            preprocessor.preprocess()
            encoder = encode.Encoder()
            tracer = trace.Tracer(encoder)
            tracer.run(
                preprocessor.code,
                globals=global_bindings,
                locals=global_bindings,
            )
            postprocessor = postprocess.Postprocessor(tracer.state)
            postprocessor.postprocess()
        except pyagram_error.PyagramError as error:
            self.data = str(error)
            self.is_error = True
        else:
            self.data = tracer.state.snapshots
            self.is_error = False

    def serialize(self):
        """
        """
        return {
            'data': self.data,
            'is_error': self.is_error,
        }
