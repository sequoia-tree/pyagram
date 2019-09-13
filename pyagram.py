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
        tracer.run(code, {}, {})
        # TODO: How to use tracer.state.hidden_flags:
        # TODO: (1) Do not display the flags in hidden_flags, but do display their sub-flags etc.
        # TODO:     (E.g. Pass in a hidden_flags argument to the ProgramState printing function.)
        # TODO: (2) Perhaps skip snapshots that correspond to opening / closing hidden flags.
        # TODO:     (But again, we want the snapshots in-between, corresponding to their sub-flags.)
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
