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

    @property
    def is_ongoing_flag_sans_frame(self):
        return isinstance(self.curr_element, PyagramFlag) and self.curr_element.frame is None

    @property
    def is_ongoing_frame(self):
        return isinstance(self.curr_element, PyagramFrame) and not self.curr_element.has_returned

    @property
    def is_complete_flag(self):
        return isinstance(self.curr_element, PyagramFlag) and self.curr_element.has_returned

    def process_frame_open(self, frame):
        """
        <summary>

        :param frame:
        :return:
        """

        # Here's the gist, but you should verify its correctness ...

        frame_type = FrameTypes.identify_frame_type(frame)
        if frame_type is FrameTypes.SRC_CALL:
            assert self.is_ongoing_flag_sans_frame
            self.curr_element = self.curr_element.add_frame(frame)
            # TODO
        elif frame_type is FrameTypes.SRC_CALL_PRECURSOR:
            assert self.is_ongoing_flag_sans_frame or self.is_ongoing_frame
            self.curr_element = self.curr_element.add_flag()
            # TODO
        elif frame_type is FrameTypes.SRC_CALL_SUCCESSOR:
            assert self.is_complete_flag
            self.curr_element = self.curr_element.close()
            # TODO
        else:
            raise FrameTypes.illegal_frame_type(frame)

    def process_frame_close(self, frame, return_value):
        """
        <summary>

        :param frame:
        :param return_value:
        :return:
        """

        # Here's the gist, but you should verify its correctness ...

        frame_type = FrameTypes.identify_frame_type(frame)
        if frame_type is FrameTypes.SRC_CALL:
            assert self.is_ongoing_frame
            self.curr_element = self.curr_element.close(return_value)
            # TODO
        elif frame_type is FrameTypes.SRC_CALL_PRECURSOR:
            assert self.is_ongoing_flag_sans_frame
            # TODO
        elif frame_type is FrameTypes.SRC_CALL_SUCCESSOR:
            assert self.is_ongoing_flag_sans_frame or self.is_ongoing_frame
            # TODO
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

    SRC_CALL_PRECURSOR = []
    SRC_CALL = []
    SRC_CALL_SUCCESSOR = []

    @staticmethod
    def identify_frame_type(frame):
        """
        <summary>

        :param frame:
        :return:
        """

        # If the frame is a SRC_CALL_PRECURSOR, it's the frame for one of the "fake" inner_lambda functions we created in wrap.py. If it's a SRC_CALL_SUCCESSOR, it's the frame for one of the "fake" outer_lambda functions we created in wrap.py.

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
        self.flags = []

    def add_flag(self):
        """
        <summary>

        :return:
        """

        # TODO: You need something like this ...
        # for flag in self.curr_element.flags:
        #     assert flag.has_returned

        flag = PyagramFlag(self)
        self.flags.append(flag)
        return flag

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
        self.has_returned = False
        self.return_value = None

    def close(self, return_value):
        """
        <summary>

        :param return_value:
        :return:
        """
        self.return_value = return_value
        self.has_returned = True
        return self.opened_by

class PyagramFlag(PyagramElement):
    """
    <summary>

    :param opened_by:
    """

    def __init__(self, opened_by):
        super().__init__(opened_by)
        self.banner = None # TODO
        self.frame = None

    def close(self):
        """
        <summary>

        :return:
        """
        return self.opened_by

    @property
    def has_returned(self):
        """
        <summary>

        :return:
        """
        return self.frame and self.frame.has_returned

    @property
    def return_value(self):
        """
        <summary>

        :return:
        """
        assert self.has_returned
        return self.frame.return_value

    def add_frame(self, frame):
        """
        <summary>

        :param frame:
        :return:
        """

        # TODO: You need something like this ...
        # assert self.banner.is_complete

        frame = PyagramFrame(self, frame)
        self.frame = frame
        return frame

class PyagramBanner:
    """
    <summary>
    """

    def __init__(self):
        pass
