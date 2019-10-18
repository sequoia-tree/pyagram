import json

import postprocess
import trace
import wrap

class Pyagram:
    """
    <summary> # Basically a Pyagram object is a list of snapshots.

    :param code:
    """

    def __init__(self, code, *, debug):
        code = wrap.wrap_calls(code)
        tracer = trace.Tracer(debug)
        global_bindings = {}
        tracer.run(code, globals=global_bindings, locals=global_bindings)
        self.snapshots = tracer.state.snapshots
        postprocess.postprocess_snapshots(self.snapshots)

    def serialize(self):
        """
        <summary>

        :return:
        """
        return json.dumps(self.snapshots)
