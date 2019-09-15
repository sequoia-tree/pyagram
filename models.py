import copy
import gc
import types

import enums
import configs

NON_REFERENT_TYPES = (int, float, str, bool)
FUNCTION_PARENTS = {}

class ProgramState:
    """
    <summary> # a mutable object representing the state of the program at the current timestep. as we go thru the program in trace.py, we will modify the ProgramState.

    :param global_frame:
    """

    def __init__(self, global_frame):
        self.global_frame = PyagramFrame(None, global_frame)
        self.curr_element = self.global_frame
        self.hidden_flags = set()
        self.tracked_objs = ProgramMemory()
        self.curr_line_no = None
        self.print_output = [] # TODO: How will you handle `print` statements?
        # TODO: Also track the current lineno. The code that handles this should probably be in ProgramState.step, but you'll want to avoid setting the self.lineno to -1 or -2 (since your fabricated lambdas have -1 and -2 for their lineno). Or you can use the negative lineno as an indicator to not make a snapshot.

    @property
    def is_ongoing_flag_sans_frame(self):
        """
        <summary>

        :return:
        """
        return isinstance(self.curr_element, PyagramFlag) and self.curr_element.frame is None

    @property
    def is_ongoing_frame(self):
        """
        <summary>

        :return:
        """
        return isinstance(self.curr_element, PyagramFrame) and not self.curr_element.has_returned

    @property
    def is_complete_flag(self):
        """
        <summary>

        :return:
        """
        return isinstance(self.curr_element, PyagramFlag) and self.curr_element.has_returned

    def __str__(self):
        """
        <summary>

        :return:
        """
        # TODO: Display the print output too!
        curr_element = f'Current element: {repr(self.curr_element)} (line {self.curr_line_no})'
        global_frame = str(self.global_frame)
        tracked_objs = str(self.tracked_objs)
        # TODO: You could make this a little prettier, especially when tracked_objs is empty.
        return '\n'.join((
            curr_element,
            '',
            global_frame,
            configs.SEPARATOR,
            '',
            tracked_objs,
            '',
        ))

    def step(self, frame, is_frame_open=False, is_frame_close=False, return_value=None):
        """
        <summary>

        :param frame:
        :param is_frame_open:
        :param is_frame_close:
        :param return_value:
        :return:
        """
        self.curr_line_no = frame.f_lineno
        if is_frame_open:
            self.process_frame_open(frame)
        if is_frame_close:
            self.process_frame_close(frame, return_value)
        self.global_frame.step(self.tracked_objs)

    def snapshot(self):
        """
        <summary> # Represents the state of the program at a particular step in time.

        :return:
        """
        # don't maintain the `snapshots` list in the ProgramState object, or else every deepcopy of the ProgramState will include a deepcopy of the entire list of past ProgramStates!
        return copy.deepcopy(self)

    def process_frame_open(self, frame):
        """
        <summary>

        :param frame:
        :return:
        """
        frame_type = enums.FrameTypes.identify_frame_type(frame)
        if frame_type is enums.FrameTypes.SRC_CALL:

            is_implicit_function_call = self.is_ongoing_frame # An "implicit call" is when the user didn't invoke the function directly. eg the user instantiates a class, and __init__ gets called implicitly.
            if is_implicit_function_call:
                self.open_pyagram_flag()
                self.open_pyagram_banner(flag_info=None) # TODO: what is the appropriate flag_info for an implicit call?
            self.open_pyagram_frame(frame)

        elif frame_type is enums.FrameTypes.SRC_CALL_PRECURSOR:
            self.open_pyagram_flag()
        elif frame_type is enums.FrameTypes.SRC_CALL_SUCCESSOR:
            pass
        else:
            raise enums.FrameTypes.illegal_frame_type(frame_type)

    def process_frame_close(self, frame, return_value):
        """
        <summary>

        :param frame:
        :param return_value:
        :return:
        """
        frame_type = enums.FrameTypes.identify_frame_type(frame)
        if frame_type is enums.FrameTypes.SRC_CALL:
            self.close_pyagram_flag_and_frame(return_value)
        elif frame_type is enums.FrameTypes.SRC_CALL_PRECURSOR:
            self.open_pyagram_banner(return_value)
        elif frame_type is enums.FrameTypes.SRC_CALL_SUCCESSOR:
            pass
        else:
            raise enums.FrameTypes.illegal_frame_type(frame_type)

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

class ProgramMemory:
    """
    <summary>
    """

    def __init__(self):
        self.object_ids = set()
        self.pyagram_objects = [] # TODO: When drawing these objects on the web-page, make sure each object in this ordered container is drawn independently of how many objects come after it. Otherwise the same object might be drawn at different locations during different steps.

    def __str__(self):
        """
        <summary>

        :return:
        """
        return '\n'.join(
            f'{id(pyagram_object.object)}: {repr(pyagram_object)}'
            for pyagram_object in self.pyagram_objects
        )

    def track(self, pyagram_object):
        """
        <summary>

        :return:
        """
        object_id = id(pyagram_object.object)
        if object_id not in self.object_ids:
            self.object_ids.add(object_id)
            self.pyagram_objects.append(pyagram_object)

    def is_tracked(self, object):
        """
        <summary>

        :param object:
        :return:
        """
        return id(object) in self.object_ids

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

    def step(self, tracked_objs):
        """
        <summary>

        :param tracked_objs:
        :return:
        """
        for flag in self.flags:
            flag.step(tracked_objs)

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
        self.is_new_frame = True
        self.is_global_frame = self.id == 0
        if self.is_global_frame:
            del frame.f_globals['__builtins__']
        else:
            self.function = get_function(frame)
        self.bindings = frame.f_locals
        self.has_returned = False
        self.return_value = None

    @property
    def parent(self):
        """
        <summary>

        :return:
        """
        assert not self.is_global_frame and self.function
        return FUNCTION_PARENTS[self.function]

    def __repr__(self):
        """
        <summary>

        :return:
        """
        return 'Global' if self.is_global_frame else f'Frame {self.id}'

    def __str__(self):
        """
        <summary>

        :return:
        """

        header = f'{repr(self)}' + ('' if self.is_global_frame else f' ({value_str(self.function)})')

        if self.bindings or self.has_returned:

            fn_len = lambda fn: lambda key_or_value: len(fn(key_or_value))
            binding = lambda key, value: f'|{key:>{max_key_length}}: {value_str(value):<{max_value_length}}|'

            max_var_key_length, ret_key_length, max_var_value_length, ret_value_length = 0, 0, 0, 0
            if self.bindings:
                max_var_key_length = fn_len(str)(max(self.bindings.keys(), key=fn_len(str)))
                max_var_value_length = fn_len(value_str)(max(self.bindings.values(), key=fn_len(value_str)))
            if self.has_returned:
                ret_key_length = len('return')
                ret_value_length = len(value_str(self.return_value))
            max_key_length = max(max_var_key_length, ret_key_length)
            max_value_length = max(max_var_value_length, ret_value_length)

            bindings = []
            if self.bindings:
                var_bindings = '\n'.join(binding(key, value) for key, value in self.bindings.items())
                bindings.append(var_bindings)
            if self.has_returned:
                ret_binding = binding('return', self.return_value)
                bindings.append(ret_binding)
            max_binding_length = max_key_length + max_value_length + 2
            bindings = '\n'.join(bindings)

        else:
            max_binding_length = max(0, len(header) - 2)
            bindings = f'|{" " * max_binding_length}|'

        separator = f'+{"-" * max_binding_length}+'

        flags = self.flags_to_text()

        return f'\n'.join((
            header,
            separator,
            bindings,
            separator,
            flags,
        ))

    def step(self, tracked_objs):
        """
        <summary>

        :param tracked_objs:
        :return:
        """
        # Two goals:
        # (1) Identify all functions floating around in memory, and enforce no two point to the same code object.
        # (2) Obtain a reference to all objects floating around in memory; wrap them in a PyagramObject instance and store the reference in the ProgramState's tracked_objs.
        pyagram_objects = {PyagramObject(object) for object in self.bindings.values()}
        if not self.is_global_frame:
            pyagram_objects.add(PyagramObject(self.function))
        if self.has_returned:
            pyagram_objects.add(PyagramObject(self.return_value))
        while pyagram_objects:
            pyagram_object = pyagram_objects.pop()
            object = pyagram_object.object
            if is_referent_type(object):
                tracked_objs.track(pyagram_object)
                if isinstance(object, types.FunctionType):
                    enforce_one_function_per_code_object(object)
                    if object not in FUNCTION_PARENTS:
                        get_parent(self, object)
                else:
                    pyagram_objects.update({
                        PyagramObject(referent)
                        for referent in gc.get_referents(object)
                        if not tracked_objs.is_tracked(referent)
                    })
        # It is desirable that once we draw an object in one step, we will draw that object in every future step even if we lose all references to it. (This is a common confusion with using environment diagrams to understand HOFs; pyagrams will not suffer the same issue.)
        self.is_new_frame = False
        super().step(tracked_objs)

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
        assert self.has_returned
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
        frame = prepend(flagpole, str(self.frame) if self.frame else '')
        return '\n'.join((
            header,
            banner,
            flags,
            frame,
        ))

    def step(self, tracked_objs):
        """
        <summary>

        :param tracked_objs:
        :return:
        """
        super().step(tracked_objs)
        if self.frame:
            self.frame.step(tracked_objs)

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

class PyagramObject:
    """
    <summary> # a hashable wrapper for potentially unhashable objects

    :param object:
    """

    def __init__(self, object):
        self.object = object

    def __repr__(self):
        """
        <summary>

        :return:
        """
        result = repr(self.object)
        if isinstance(self.object, types.FunctionType):
            result = ' '.join((
                result,
                f'[p = {repr(FUNCTION_PARENTS[self.object])}]'
            ))
        return result

def get_parent(frame, function):
    """
    <summary>

    :param frame:
    :param function:
    :return:
    """
    if not frame.is_global_frame and frame.is_new_frame:
        parent = frame.opened_by
        while isinstance(parent, PyagramFlag):
            parent = parent.opened_by
    else:
        parent = frame
    FUNCTION_PARENTS[function] = parent

def get_function(frame):
    """
    <summary>

    :param frame:
    :return:
    """
    function = None
    for referrer in gc.get_referrers(frame.f_code):
        if isinstance(referrer, types.FunctionType):
            assert function is None, f'multiple functions refer to code object {frame.f_code}'
            function = referrer
    assert function is not None
    return function

def is_referent_type(object):
    """
    <summary>

    :param object:
    :return:
    """
    return not isinstance(object, NON_REFERENT_TYPES)

def enforce_one_function_per_code_object(function):
    """
    <summary>

    :param function:
    :return:
    """
    old_code = function.__code__
    new_code = types.CodeType(
        old_code.co_argcount,
        old_code.co_kwonlyargcount,
        old_code.co_nlocals,
        old_code.co_stacksize,
        old_code.co_flags,
        old_code.co_code,
        old_code.co_consts,
        old_code.co_names,
        old_code.co_varnames,
        old_code.co_filename,
        old_code.co_name,
        old_code.co_firstlineno,
        old_code.co_lnotab,
        old_code.co_freevars,
        old_code.co_cellvars,
    )
    function.__code__ = new_code

def value_str(object):
    """
    <summary>

    :param object:
    :return:
    """
    return f'*{id(object)}' if is_referent_type(object) else repr(object)

def prepend(prefix, text):
    """
    <summary> # prepend prefix to every line in text

    :param text:
    :param prefix:
    :return:
    """
    return prefix + text.replace('\n', f'\n{prefix}')

# TODO: Split models.py into state.py and pyagram_element.py?
# TODO: And put the functions that aren't in classes (e.g. `get_function`) in their own file, utils.py?
# TODO: Rename configs.py?
