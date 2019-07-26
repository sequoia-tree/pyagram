import wrap
import trace

TERMINAL_WIDTH = 80

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

    def display(self):
        """
        <summary>

        :return:
        """
        for snapshot in self.snapshots:
            print(snapshot)
            print('-' * TERMINAL_WIDTH)
            input()
