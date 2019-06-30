import wrap
import trace

class Pyagram:
    """
    <summary> # Basically a Pyagram object is a list of snapshot objects.

    :param code:
    """

    def __init__(self, code):
        code = wrap.wrap_calls(code)
        tracer = trace.Tracer()
        tracer.run(code, {}, {})
        self.snapshots = tracer.snapshots
