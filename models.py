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
        self.hidden_flags = set()
        self.print_output = [] # TODO: How will you handle `print` statements?
        # TODO: Also track the current lineno. The code that handles this should probably be in ProgramState.step, but you'll want to avoid setting the self.lineno to -1 or -2 (since your fabricated lambdas have -1 and -2 for their lineno).

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

    def process_frame_open(self, frame):
        """
        <summary>

        :param frame:
        :return:
        """
        frame_type = FrameTypes.identify_frame_type(frame)
        if frame_type is FrameTypes.SRC_CALL:

            is_implicit_function_call = self.is_ongoing_frame # An "implicit call" is when the user didn't invoke the function directly. eg the user instantiates a class, and __init__ gets called implicitly.
            if is_implicit_function_call:
                self.open_pyagram_flag()
                self.open_pyagram_banner(flag_info=None) # TODO: what is the appropriate flag_info for an implicit call?
            self.open_pyagram_frame(frame)

        elif frame_type is FrameTypes.SRC_CALL_PRECURSOR:
            self.open_pyagram_flag()
        elif frame_type is FrameTypes.SRC_CALL_SUCCESSOR:
            pass
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
            self.close_pyagram_flag_and_frame(return_value)
        elif frame_type is FrameTypes.SRC_CALL_PRECURSOR:
            self.open_pyagram_banner(return_value)
        elif frame_type is FrameTypes.SRC_CALL_SUCCESSOR:
            pass
        else:
            raise FrameTypes.illegal_frame_type(frame)

    def open_pyagram_flag(self):
        # TODO: Docstrings for this and the other methods below it.
        assert self.is_ongoing_flag_sans_frame or self.is_ongoing_frame
        self.curr_element = self.curr_element.add_flag()

    def open_pyagram_banner(self, flag_info):
        assert self.is_ongoing_flag_sans_frame
        pass # TODO: wrap.py's flag_info is accessible through `flag_info`.

    def open_pyagram_frame(self, frame):
        assert self.is_ongoing_flag_sans_frame
        self.curr_element = self.curr_element.add_frame(frame)

    def close_pyagram_flag_and_frame(self, return_value):
        if self.is_ongoing_flag_sans_frame:
            # this flag has no frame; it should not get visualized

            # The problem is that when you don't write your own __init__ function, bdb doesn't open a frame for object-instantiation! (So you're making the flag, assuming bdb will open the frame, but that never happens ... !)
            # Most straightforward solution: (1) AND (2)
            # (1): Whenever you close a flag that doesn't have its own frame, delete it. (But do not delete the sub-flags! Those might still be useful.)
            # (2): In your book say __init__ only gets called if it is indeed defined.

            flag = self.curr_element
            self.hidden_flags.add(flag)
            self.curr_element = flag.opened_by
        elif self.is_ongoing_frame:

            # close frame and then the flag
            is_global_frame = self.curr_element is self.global_frame
            self.curr_element = self.curr_element.close(return_value)
            if not is_global_frame:
                self.curr_element = self.curr_element.close()
        else:
            assert False

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

        # for flag in self.curr_element.flags:
        #     assert flag.has_returned
        # But I guess it's only necessary to check the most recent flag has been closed. This particular code (the one above, that is) is a bit redundant.
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
        # Perhaps return 'Global' if self.id == 0 else f'Frame {self.id}'
        return f'Frame {self.id}'

    def __str__(self):
        """
        <summary>

        :return:
        """

        header = f'{repr(self)} (parent: {repr(self.parent)})'

        fn_len = lambda fn: lambda key_or_value: len(fn(key_or_value))
        binding = lambda key, value: f'|{key:>{max_key_length}}: {repr(value):<{max_value_length}}|'

        max_key_length = len('return')
        max_value_length = 1
        if self.bindings: # TODO: Clean up this if/else statement.
            max_key_length = max(
                max_key_length,
                fn_len(str)(max(self.bindings.keys(), key=fn_len(str))),
            )
            max_value_length = max(
                max_value_length,
                fn_len(repr)(max(self.bindings.values(), key=fn_len(repr))),
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
        # TODO: Or do it in ProgramState.open_pyagram_frame since that's where the other asserts are

        frame = PyagramFrame(self, frame)
        self.frame = frame
        return frame

class PyagramBanner:
    """
    <summary>
    """

    pass

def prepend(prefix, text):
    """
    <summary> # prepend prefix to every line in text

    :param text:
    :param prefix:
    :return:
    """
    return prefix + text.replace('\n', f'\n{prefix}')

# TODO: Split models.py into state.py, pyagram_element.py, and enum.py?
