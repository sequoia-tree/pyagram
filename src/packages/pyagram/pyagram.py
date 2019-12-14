from . import postprocessor
from . import preprocess
from . import trace

class Pyagram:
    """
    A diagram describing the step-by-step execution of a snippet of Python code.

    After initialization, :self.snapshots: is a list of serializable snapshots. Each such snapshot
    encodes the state of the pyagram at a particular step during the execution of the input code.

    :param code: The snippet of Python code for which to create the pyagram.
    :param debug: Whether or not to enable debugging features such as on-the-fly printing of the
      pyagram during its construction.
    """

    def __init__(self, code, *, debug):
        code = preprocess.preprocess_code(code) # TODO: Turn `preprocess` into `Preprocessor` for parallelism.
        tracer = trace.Tracer(debug)
        global_bindings = {}
        tracer.run(code, globals=global_bindings, locals=global_bindings)
        postprocessor.Postprocessor(tracer.state).postprocess()
        self.snapshots = tracer.state.snapshots
