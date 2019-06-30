import copy

import wrap

class ProgramState:
    """
    <summary> # a mutable object representing the state of the program at the current timestep. as we go thru the program in trace.py, we will modify the ProgramState.

    :param global_frame:
    """

    def __init__(self, global_frame):
        self.global_frame = PyagramFrame(None, global_frame)
        self.curr_element = self.global_frame
        self.print_output = [] # TODO: How will you handle `print` statements?
        # TODO: I think the ProgramState should also track what line we're on. That way we can draw an arrow that points to the last-executed line. The code that handles this should probably be in ProgramState.step, but you'll want to avoid setting the self.lineno to -1 or -2 (since your fabricated lambdas have -1 and -2 for their lineno).

    def process_frame_open(self, frame):
        """
        <summary>

        :param frame:
        :return:
        """

        # Open SRC_CALL_PRECURSOR frame:
        #   Start a flag with ID `id` and give it a banner.
        #   self.curr_element: {any open flag with no terminal frame yet, any open frame}
        # Open SRC_CALL frame:
        #   Start a terminal frame for the current flag.
        #   self.curr_element: {any open flag with no terminal frame yet}
        # OPEN SRC_CALL_SUCCESSOR frame:
        #   End the flag with ID `id`.
        #   self.curr_element: {any closed frame}

        # Close SRC_CALL_PRECURSOR frame:
        #   Do nothing. This should come right after transitioning into a new flag.
        #   self.curr_element: {the flag that we just opened}
        # Close SRC_CALL frame:
        #   End the frame for the current flag and record its return value.
        #   self.curr_element: {any open frame}
        # Close SRC_CALL_SUCCESSOR frame:
        #   Do nothing. This should come right after closing the flag with ID `id`.
        #   self.curr_element: {the flag that we just closed}

        frame_type = FrameTypes.identify_frame_type(frame)
        if frame_type is FrameTypes.SRC_CALL:
            pass # TODO
        elif frame_type is FrameTypes.SRC_CALL_PRECURSOR:
            pass # TODO
        elif frame_type is FrameTypes.SRC_CALL_SUCCESSOR:
            pass # TODO
        else:
            raise FrameTypes.illegal_frame_type(frame)

    def process_frame_close(self, frame, return_value):
        """
        <summary>

        :param frame:
        :param return_value:
        :return:
        """
        frame_type = FrameTypes.identify_frame_type(frame)
        if frame_type is FrameTypes.SRC_CALL:
            pass # TODO
        elif frame_type is FrameTypes.SRC_CALL_PRECURSOR:
            pass # TODO
        elif frame_type is FrameTypes.SRC_CALL_SUCCESSOR:
            pass # TODO
        else:
            raise FrameTypes.illegal_frame_type(frame)

class ProgramStateSnapshot:
    """
    <summary> # Represents the state of the program at a particular step in time.

    :param state: a ProgramState instance to take snapshot of
    """

    def __init__(self, state):
        # self.global_frame = copy.deepcopy(state.global_frame)
        # self.print_output = copy.deepcopy(state.print_output)
        pass
        # TODO: Basically make a deepcopy of the `state` object.
        # Note that a PyagramFrame's self.bindings updates automatically.
        pass

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

class FrameTypes:
    """
    <summary> # basically this is like an Enum class
    """

    SRC_CALL_PRECURSOR = 0
    SRC_CALL = 1
    SRC_CALL_SUCCESSOR = 2

    @staticmethod
    def identify_frame_type(frame):
        """
        <summary>

        :param frame:
        :return:
        """
        lineno = frame.f_lineno
        if lineno == wrap.INNER_CALL_LINENO:
            return FrameTypes.SRC_CALL_PRECURSOR
        if lineno == wrap.OUTER_CALL_LINENO:
            return FrameTypes.SRC_CALL_SUCCESSOR
        assert 0 < lineno
        return FrameTypes.SRC_CALL

    @staticmethod
    def illegal_frame_type(frame):
        return ValueError(f'frame object {frame} has no pyagram counterpart')

class PyagramElement:
    """
    <summary>
    """

    def __init__(self, opened_by):
        self.opened_by = opened_by

class PyagramFrame(PyagramElement):
    """
    <summary>

    :param opened_by:
    :param frame: the corresponding built-in frame object
    """

    def __init__(self, opened_by, frame):
        super().__init__(opened_by)
        self.parent = None # TODO
        self.bindings = frame.locals
        self.flags = []
        self.return_value = None
        self.has_returned = False

    def close(self, return_value):
        """
        <summary>

        :param return_value:
        :return:
        """
        self.return_value = return_value
        self.has_returned = True

class PyagramFlag(PyagramElement):
    """
    <summary>

    :param opened_by:
    """

    def __init__(self):
        super().__init__(opened_by)
        self.banner = None # TODO
        self.flags = []
        self.frame = None

    @property
    def has_returned(self):
        """
        <summary>

        :return:
        """
        return self.frame and self.frame.has_returned

class PyagramBanner:
    """
    <summary>
    """

    def __init__(self):
        pass
