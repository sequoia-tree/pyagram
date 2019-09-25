import trace
import utils
import wrap

class Pyagram:
    """
    <summary> # Basically a Pyagram object is a list of snapshots.

    :param code:
    """

    def __init__(self, code, debug=False):
        code = wrap.wrap_calls(code)
        tracer = trace.Tracer(debug)
        global_bindings = {}
        tracer.run(code, globals=global_bindings, locals=global_bindings)
        self.snapshots = tracer.snapshots
        utils.interpolate_flag_banners(self.snapshots, tracer.state)
