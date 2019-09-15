import wrap
import trace

import configs

class Pyagram:
    """
    <summary> # Basically a Pyagram object is a list of snapshots.

    :param code:
    """

    def __init__(self, code):
        code = wrap.wrap_calls(code)
        tracer = trace.Tracer()
        global_bindings = {}
        tracer.run(code, globals=global_bindings, locals=global_bindings)
        self.snapshots = tracer.snapshots

    def display(self):
        """
        <summary>

        :return:
        """
        for snapshot in self.snapshots:
            diagram = str(snapshot)
            diagram_height = diagram.count('\n') + 1
            padding = configs.TERMINAL_HEIGHT - (diagram_height + 2)
            print(diagram)
            print(configs.SEPARATOR)
            if padding > 0:
                print('\n' * (padding - 1))
            input()
