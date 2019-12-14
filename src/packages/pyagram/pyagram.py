from . import encode
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
        num_lines, global_bindings = len(code.split('\n')), {}
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
        self.snapshots = tracer.state.snapshots
