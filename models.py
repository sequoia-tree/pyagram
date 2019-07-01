import copy

import wrap

TERMINAL_WIDTH = 80

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

    def __str__(self):
        """
        <summary>

        :return:
        """
        # TODO: Display the line number and the print output too!
        curr_element = f'Current element: {repr(self.curr_element)}'
        global_frame = str(self.global_frame)
        return '\n'.join((
            curr_element,
            '',
            global_frame,
        ))

    def display(self):
        """
        <summary>

        :return:
        """
        print(self)
        print('-' * TERMINAL_WIDTH)
        input()

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
        elif frame_type is FrameTypes.SRC_CALL_PRECURSOR:
            assert self.is_ongoing_flag_sans_frame or self.is_ongoing_frame
            self.curr_element = self.curr_element.add_flag()
        elif frame_type is FrameTypes.SRC_CALL_SUCCESSOR:
            assert self.is_complete_flag
            self.curr_element = self.curr_element.close()
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
        elif frame_type is FrameTypes.SRC_CALL_PRECURSOR:
            assert self.is_ongoing_flag_sans_frame
        elif frame_type is FrameTypes.SRC_CALL_SUCCESSOR:
            assert self.is_ongoing_flag_sans_frame or self.is_ongoing_frame
        else:
            raise FrameTypes.illegal_frame_type(frame)

    def snapshot(self):
        """
        <summary> # Represents the state of the program at a particular step in time.

        :return:
        """
        return copy.deepcopy(self)

class FrameTypes:
    """
    <summary> # basically this is like an Enum class
    """

    SRC_CALL_PRECURSOR = object()
    SRC_CALL = object()
    SRC_CALL_SUCCESSOR = object()

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
        cls = type(self)
        self.id = cls.COUNT
        cls.COUNT += 1
        self.opened_by = opened_by
        self.flags = []

    def flags_to_text(self):
        """
        <summary>

        :return:
        """
        return '\n'.join(f'\n{flag}' for flag in self.flags) + ('\n' if self.flags else '')

    def add_flag(self):
        """
        <summary>

        :return:
        """

        # TODO: You need something like this ...
        # for flag in self.curr_element.flags:
        #     assert flag.has_returned
        # Though I guess it's only necessary to check the most recent flag has been closed. This particular code is a bit redundant.
        # For example:
        if self.flags:
            assert self.flags[-1].has_returned

        flag = PyagramFlag(self)
        self.flags.append(flag)
        return flag

class PyagramFrame(PyagramElement):
    """
    <summary>

    :param opened_by:
    :param frame: the corresponding built-in frame object
    """

    COUNT = 0

    def __init__(self, opened_by, frame):
        super().__init__(opened_by)
        self.parent = None # TODO
        self.bindings = frame.f_locals
        self.has_returned = False
        self.return_value = None

    def __repr__(self):
        """
        <summary>

        :return:
        """
        return f'Frame {self.id}'

    def __str__(self):
        """
        <summary>

        :return:
        """

        header = f'{repr(self)} (parent: {repr(self.parent)})'

        str_len = lambda key_or_value: len(str(key_or_value))
        binding = lambda key, value: f'|{key:>{max_key_length}}: {str(value):<{max_value_length}}|'


        max_key_length = len('return')
        max_value_length = 1
        if self.bindings: # TODO: Clean up this if/else statement.
            max_key_length = max(
                max_key_length,
                str_len(max(self.bindings.keys(), key=str_len)),
            )
            max_value_length = max(
                max_value_length,
                str_len(max(self.bindings.values(), key=str_len)),
            )
            bindings = '\n'.join(binding(key, value) for key, value in self.bindings.items())
        else:
            bindings = f'|{" ":{max_key_length + max_value_length + 2}}|'

        if self.has_returned:
            bindings = '\n'.join((bindings, binding('return', self.return_value)))
        separator = f'+{"-" * (max_key_length + max_value_length + 2)}+'

        flags = self.flags_to_text()

        return f'\n'.join((
            header,
            separator,
            bindings,
            separator,
            flags,
        ))

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

    COUNT = 0

    def __init__(self, opened_by):
        super().__init__(opened_by)
        self.banner = None # TODO
        self.frame = None

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
        assert self.has_returned # TODO: Maybe throw a more appropriate exception.
        return self.frame.return_value

    def __repr__(self):
        """
        <summary>

        :return:
        """
        return f'Flag {self.id}'

    def __str__(self, prefix=''):
        """
        <summary>

        :return:
        """

        flagpole = '| '

        header = f'{repr(self)}'
        banner = '+--------+\n| BANNER |\n+--------+' # TODO
        flags = prepend(flagpole, self.flags_to_text())
        frame = prepend(flagpole, f'{self.frame}')
        return '\n'.join((
            header,
            banner,
            flags,
            frame,
        ))

    def close(self):
        """
        <summary>

        :return:
        """
        return self.opened_by

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

    pass

# TODO: Split models.py into state.py, pyagram_element.py, and enum.py?

def prepend(prefix, text):
    """
    <summary> # prepend prefix to every line in text

    :param text:
    :param prefix:
    :return:
    """
    return prefix + text.replace('\n', f'\n{prefix}')
