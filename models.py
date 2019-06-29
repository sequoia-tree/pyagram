import copy

class ProgramState:
    """
    <summary> # a mutable object representing the state of the program at the current timestep. as we go thru the program in trace.py, we will modify the ProgramState.

    :param global_frame:
    """

    def __init__(self, global_frame):
        self.global_frame = PyagramFrame(global_frame)
        self.print_output = [] # TODO: How will you handle `print` statements?

    def get_frame(self, frame):
        """
        <summary>

        :param frame:
        :return:
        """
        return # TODO: maps built-in frame obj to corresponding PyagramFrame obj

class ProgramStateSnapshot:
    """
    <summary> # Represents the state of the program at a particular step in time.

    :param state: a ProgramState instance to take snapshot of
    """

    def __init__(self, state):
        self.global_frame = copy.deepcopy(state.global_frame)
        self.print_output = copy.deepcopy(state.print_output)

    def __repr__(self):
        """
        <summary>

        :return:
        """
        # for num, frame in enumerate(self.frames):
        #     print(f'Frame {num}: {frame.f_locals}')
        #     if self.return_values.get(frame, False):
        #         print(f'\tReturn: {repr(self.return_values[frame])}')
        # print('')
        return '' # TODO

class PyagramFrame:
    """
    <summary>

    :param frame: the corresponding built-in frame object
    """

    def __init__(self, frame):
        # TODO: Use `frame` somehow. (I think we only need to track frame.locals?)
        self.return_value = None
        self.has_returned = False

    def terminate(self, return_value):
        """
        <summary>

        :param return_value:
        :return:
        """
        self.return_value = return_value
        self.has_returned = True

class PyagramFlag:
    """
    <summary>
    """

    def __init__(self):
        pass
