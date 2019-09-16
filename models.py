import copy
import gc
import types

import display
import enums
import utils

class ProgramState:
    """
    <summary> # a mutable object representing the state of the program at the current timestep. as we go thru the program in trace.py, we will modify the ProgramState.

    :param global_frame:
    """

    def __init__(self, global_frame):
        self.global_frame = PyagramFrame(None, global_frame)
        self.curr_element = self.global_frame
        self.tracked_objs = ProgramMemory()
        self.curr_line_no = None
        self.print_output = [] # TODO: How will you handle `print` statements?

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
        curr_element = f'Current element: {repr(self.curr_element)} (line {self.curr_line_no})'
        global_frame_header = display.separator('program execution')
        global_frame = str(self.global_frame)
        tracked_objs_header = display.separator('objects in memory')
        tracked_objs = str(self.tracked_objs)
        print_output_header = display.separator('print output')
        print_output = '\n'.join(self.print_output)
        return '\n'.join((
            curr_element,
            '',
            global_frame_header,
            '',
            global_frame,
            tracked_objs_header + (f'\n\n{tracked_objs}\n' if tracked_objs else ''),
            print_output_header + (f'\n{print_output}' if print_output else ''),
            display.separator(),
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

            is_implicit = self.is_ongoing_frame # An "implicit call" is when the user didn't invoke the function directly. eg the user instantiates a class, and __init__ gets called implicitly.
            if is_implicit:
                self.open_pyagram_flag(flag_info=None) # TODO: what is the appropriate flag_info for an implicit call?
            self.open_pyagram_frame(frame, is_implicit)

        elif frame_type is enums.FrameTypes.SRC_CALL_PRECURSOR:
            pass
        elif frame_type is enums.FrameTypes.SRC_CALL_SUCCESSOR:
            self.close_pyagram_flag()
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
            self.close_pyagram_frame(return_value)
        elif frame_type is enums.FrameTypes.SRC_CALL_PRECURSOR:
            self.open_pyagram_flag(return_value)
        elif frame_type is enums.FrameTypes.SRC_CALL_SUCCESSOR:
            pass
        else:
            raise enums.FrameTypes.illegal_frame_type(frame_type)

    def open_pyagram_flag(self, flag_info):
        """
        <summary>

        :param flag_info:
        :return:
        """
        # TODO: wrap.py's flag_info is accessible through `flag_info`.
        assert self.is_ongoing_flag_sans_frame or self.is_ongoing_frame
        self.curr_element = self.curr_element.add_flag()

    def open_pyagram_frame(self, frame, is_implicit):
        """
        <summary>

        :param frame:
        :param is_implicit:
        :return:
        """
        assert self.is_ongoing_flag_sans_frame
        self.curr_element = self.curr_element.add_frame(frame, is_implicit)

    def close_pyagram_flag(self):
        """
        <summary>

        :return:
        """
        assert self.is_complete_flag or self.is_ongoing_flag_sans_frame
        if self.is_ongoing_flag_sans_frame:

            # The problem is that when you call a built-in function (like append or min), or when you don't write your own __init__ function, bdb doesn't open a frame! (So you're making the flag, assuming bdb will open the frame, but that never happens ... !)
            # Most straightforward solution: (1) AND (2)
            # (1): Whenever you close a flag that doesn't have its own frame, give it a frame.
            # (2): In your book say __init__ only gets called if it is indeed defined.

            pass

            # TODO: Instead of this HIDDEN_FLAGS nonsense, add a 'fake' frame that displays the return value.
            # TODO: To get the return value, you don't actually need the frame! (Which is good, since BDB doesn't give us access to the frame.) You can get it upon the closing of the frame for the outer-lambda wrapper (see `wrap.py`) instead, as its return value is the same!

        self.curr_element = self.curr_element.close()

    def close_pyagram_frame(self, return_value):
        """
        <summary>

        :param return_value:
        :return:
        """
        assert self.is_ongoing_frame
        is_implicit = self.curr_element.is_implicit
        self.curr_element = self.curr_element.close(return_value)
        if is_implicit:
            self.curr_element = self.curr_element.close()

class ProgramMemory:
    """
    <summary>
    """

    def __init__(self):
        self.function_parents = {}
        self.object_ids = set()
        self.objects = [] # TODO: Make sure that every object gets displayed in the same place on the web-page, across different steps of the visualization. One approach: render the last step first (since it will have all the objects visualized); then make sure every object gets drawn in the same place in every previous step.

    def __str__(self):
        """
        <summary>

        :return:
        """
        return '\n'.join(
            f'{id(object)}: {display.mem_str(object, self.function_parents)}'
            for object in self.objects
        )

    def track(self, object):
        """
        <summary>

        :return:
        """
        object_id = id(object)
        if object_id not in self.object_ids:
            self.object_ids.add(object_id)
            self.objects.append(object)

    def is_tracked(self, object):
        """
        <summary>

        :param object:
        :return:
        """
        return id(object) in self.object_ids

    def record_parent(self, frame, function):
        """
        <summary>

        :param frame:
        :param function:
        :return:
        """
        if function not in self.function_parents:
            if not frame.is_global_frame and frame.is_new_frame:
                parent = frame.opened_by
                while isinstance(parent, PyagramFlag):
                    parent = parent.opened_by
            else:
                parent = frame
            self.function_parents[function] = parent

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

    def add_flag(self):
        """
        <summary>

        :return:
        """

        # TODO: If you managed to give a 'fake' frame to those flags which otherwise wouldn't have one (see close_pyagram_flag) then uncomment the sanity check below.
        # if self.flags:
        #     assert self.flags[-1].has_returned

        flag = PyagramFlag(self)
        self.flags.append(flag)
        return flag

    def flags_to_text(self):
        """
        <summary>

        :return:
        """
        result = '\n'.join(f'\n{flag}' for flag in self.flags)
        result = result + '\n' if result.strip('\n') else ''
        return result

class PyagramFlag(PyagramElement):
    """
    <summary>

    :param opened_by:
    """

    COUNT = 0

    def __init__(self, opened_by):
        super().__init__(opened_by)
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
        flags = display.prepend(flagpole, self.flags_to_text())
        frame = display.prepend(flagpole, str(self.frame) if self.frame else '')
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

    def add_frame(self, frame, is_implicit):
        """
        <summary>

        :param frame:
        :return:
        """

        # TODO: You need something like this ...
        # assert self.banner.is_complete
        # TODO: Or do it in ProgramState.open_pyagram_frame since that's where the other asserts are

        frame = PyagramFrame(self, frame, is_implicit)
        self.frame = frame
        return frame

class PyagramFrame(PyagramElement):
    """
    <summary>

    :param opened_by:
    :param frame: the corresponding built-in frame object
    """

    COUNT = 0

    def __init__(self, opened_by, frame, is_implicit=False):
        super().__init__(opened_by)
        self.is_new_frame = True
        self.is_implicit = is_implicit
        if self.is_global_frame:
            del frame.f_globals['__builtins__']
        else:
            self.function = utils.get_function(frame)
        self.bindings = frame.f_locals
        self.has_returned = False
        self.return_value = None

    @property
    def is_global_frame(self):
        """
        <summary>

        :return:
        """
        return self.opened_by is None

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
        return_key = 'return'
        header = f'{repr(self)}' + ('' if self.is_global_frame else f' ({display.obj_str(self.function)})')
        if self.bindings or self.has_returned:
            str_len = utils.mapped_len(str)
            obj_str_len = utils.mapped_len(display.obj_str)
            max_var_key_len, ret_key_len, max_var_value_len, ret_value_len = 0, 0, 0, 0
            if self.bindings:
                max_var_key_len = str_len(max(self.bindings.keys(), key=str_len))
                max_var_value_len = obj_str_len(max(self.bindings.values(), key=obj_str_len))
            if self.has_returned:
                ret_key_len = len(str(return_key))
                ret_value_len = len(display.obj_str(self.return_value))
            max_key_len = max(max_var_key_len, ret_key_len)
            max_value_len = max(max_var_value_len, ret_value_len)
            binding = display.get_binding(max_key_len, max_value_len)
            bindings = []
            if self.bindings:
                var_bindings = '\n'.join(binding(key, value) for key, value in self.bindings.items())
                bindings.append(var_bindings)
            if self.has_returned:
                ret_binding = binding(return_key, self.return_value)
                bindings.append(ret_binding)
            max_binding_len = max_key_len + max_value_len + 2
            bindings = '\n'.join(bindings)
        else:
            max_binding_len = max(0, len(header) - 2)
            bindings = f'|{" " * max_binding_len}|'
        separator = f'+{"-" * max_binding_len}+'
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
        # (2) Obtain a reference to all objects floating around in memory; store said references in the ProgramState's tracked_objs.
        objects = list(self.bindings.values())
        if not self.is_global_frame:
            objects.append(self.function)
        if self.has_returned:
            objects.append(self.return_value)
        while objects:
            object = objects.pop()
            if utils.is_referent_type(object):
                tracked_objs.track(object)
                if isinstance(object, types.FunctionType):
                    utils.enforce_one_function_per_code_object(object)
                    tracked_objs.record_parent(self, object)
                    referents = utils.get_defaults(object)
                else:
                    referents = list(gc.get_referents(object))
                objects.extend(
                    referent
                    for referent in referents
                    if not tracked_objs.is_tracked(referent)
                )
        # It is desirable that once we draw an object in one step, we will draw that object in every future step even if we lose all references to it. (This is a common confusion with using environment diagrams to understand HOFs; pyagrams will not suffer the same issue.)
        self.is_new_frame = False
        super().step(tracked_objs)

    def close(self, return_value):
        """
        <summary>

        :param return_value:
        :return:
        """
        if not self.is_global_frame:
            self.return_value = return_value
            self.has_returned = True
        return self.opened_by

# TODO: So it seems the signature has the REAL default objects' IDs; the ones displayed in the 'OBJECTS IN MEMORY' section are actually FAKE. The problem is that when you make a deepcopy of the current state you also make a deepcopy of each object -- which produces the fake IDs, as well as the illusion that each object's ID changes over time. What you should do:
#   (*) Upon opening the banner, the PyagramFlag should have (1) the string of code for the function being called, and (2) the string of code for all the arguments. (The latter should be one long string of code, not many small ones.)
#   (*) Do away with this deepcopying nonsense.
#   (*) Instead of making a deepcopy, `snapshot` should return a JSON!
#   (*) Then, once you have a JSON at the very end, you can go back and add the flag banner values. (Between FUNCTION_PARENTS.keys() -- which should be completely filled out, by the end of the diagram -- as well as inspect.signature, you should be able to do this just fine I think. (How?))

# TODO: Move PyagramElement and its subclasses into pyagram_elements.py, and the state stuff into program_state.py?
