import gc

from . import display
from . import encode
from . import pyagram_types
from . import utils

class PyagramElement:
    """
    An element of a pyagram, during the completion of which, it is possible to encounter multiple
    function calls -- and which may thus cause the instantiation of multiple flags.
    """

    def __init__(self, opened_by, state):
        self.opened_by = opened_by
        self.state = self.opened_by.state if state is None else state
        if isinstance(self, PyagramFlag):
            self.id = self.state.num_pyagram_flags
            self.state.num_pyagram_flags += 1
        elif isinstance(self, PyagramFrame):
            self.id = self.state.num_pyagram_frames
            self.state.num_pyagram_frames += 1
        else:
            raise TypeError()
        self.flags = []

    def step(self):
        """
        <summary>

        :return:
        """
        for flag in self.flags:
            flag.step()

    def add_flag(self, banner):
        """
        <summary>

        :return:
        """
        flag = PyagramFlag(self, banner)
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
    An element of a pyagram which represents the application of a not-yet-evaluated function to a
    set of not-yet-evaluated arguments.
    
    Upon opening a flag, the following occurs:
    1. The flag's banner is made to bear the code corresponding to the function call in question.
    2. The function is evaluated, and its value written on the banner beneath the code
       corresponding to the function of the function call.
    3. The arguments are evaluated, one at a time, and their values written on the banner beneath
       the code corresponding to the arguments of the function call.
    4. A frame is opened, for the application of the now-evaluated function to the now-evaluated
       arguments. The completion of the frame marks the completion of the flag as well.
    If a new function call is encountered before the banner is complete, a new flag is opened
    within the flag in question. The new flag corresponds to the new function call, and until it is
    completed, progress on the flag in question comes to a stand-still.

    :param opened_by: The PyagramElement which opened the flag, i.e. the
      :state.program_state.curr_element: in the step immediately preceding that in which the flag
      is instantiated.
    """

    def __init__(self, opened_by, banner, *, state=None):
        super().__init__(opened_by, state)
        self.is_new_flag = True
        banner_elements, banner_bindings = banner
        utils.concatenate_adjacent_strings(banner_elements)
        self.banner_elements = banner_elements
        self.banner_bindings = banner_bindings
        self.banner_binding_index = 0
        self.positional_arg_index = 0
        self.frame = None

    @property
    def banner_is_complete(self):
        """
        <summary>

        :return:
        """
        return self.banner_binding_index == len(self.banner_bindings)

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

        function_call = ''.join((
            banner_element if isinstance(banner_element, str) else banner_element[0]
            for banner_element in self.banner_elements
        ))
        separator = f'+{"-" * (len(function_call) + 2)}+'
        banner = f'{separator}\n| {function_call} |\n{separator}'

        flags = display.prepend(flagpole, self.flags_to_text())
        frame = display.prepend(flagpole, str(self.frame) if self.frame else '')
        return '\n'.join((
            header,
            banner,
            flags,
            frame,
        ))
    
    def step(self):
        """
        <summary>

        :return:
        """
        # Fill in all banner bindings up until the next one that's a call.

        if not self.banner_is_complete:

            if self is self.state.program_state.curr_element:
                if self.is_new_flag or self.has_processed_subflag_since_prev_eval:
                    
                    if not self.is_new_flag:
                        self.evaluate_next_banner_binding(True)
                    next_binding_might_not_be_call = True
                    while next_binding_might_not_be_call and not self.banner_is_complete:
                        next_binding_might_not_be_call = self.evaluate_next_banner_binding(False)
                
                self.has_processed_subflag_since_prev_eval = False
            else:
                self.has_processed_subflag_since_prev_eval = True


        if self.frame:
            self.frame.step()
        self.is_new_flag = False
        super().step()

    def snapshot(self):
        """
        <summary>

        :return:
        """
        return {
            'is_curr_element': self is self.state.program_state.curr_element,
            'pyagram_flag': self,
            'banner_binding_index': self.banner_binding_index,
            'frame': None if self.frame is None else self.frame.snapshot(),
            'flags': [flag.snapshot() for flag in self.flags],
        }
    
    def evaluate_next_banner_binding(self, expect_call):
        """
        <summary>
        
        :return:
        """
        # Examine the next binding.
        # If it turns out to be a call: (1) DON'T evaluate it. (2) Return False.
        # Else: (1) Evaluate the binding. (2) Return True.
        # Also return False if the banner gets completed.

        binding = self.banner_bindings[self.banner_binding_index]
        is_unsupported_binding = binding is None
        if is_unsupported_binding:
            self.state.snapshot()
            while not self.banner_is_complete:
                self.banner_bindings[self.banner_binding_index] = utils.BANNER_UNSUPPORTED_CODE
                self.banner_binding_index += 1
            return False
        else:
            is_call, param_if_known = binding
            if is_call and not expect_call:
                return False
            else:
                self.state.snapshot()
                if param_if_known is None:
                    next_binding_is_func = self.banner_binding_index == 0
                    if next_binding_is_func:
                        self.banner_bindings[self.banner_binding_index] = utils.BANNER_FUNCTION_CODE
                    else:
                        self.banner_bindings[self.banner_binding_index] = self.positional_arg_index
                        self.positional_arg_index += 1
                else:
                    self.banner_bindings[self.banner_binding_index] = param_if_known
                self.banner_binding_index += 1
                return True

    def add_frame(self, frame, is_implicit):
        """
        <summary>

        :param frame:
        :return:
        """
        assert self.banner_is_complete
        frame = PyagramFrame(self, frame, is_implicit=is_implicit)
        self.frame = frame
        return frame

    def close(self):
        """
        <summary>

        :return:
        """
        return self.opened_by

class PyagramFrame(PyagramElement):
    """
    An element of a pyagram which represents the application of an already-evaluated function to a
    set of already-evaluated arguments.
    
    Upon opening a frame, the following occurs:
    1. The function's parameters are bound to their respective arguments inside the frame.
    2. The function's code is executed one step at a time, and the frame's bindings are
       correspondingly updated.
    3. The function's execution terminates, and the return value is written in the frame, thereby
       completing the frame.
    If a new function call is encountered before the frame is complete, a new flag is opened
    beneath the frame in question. The new flag corresponds to the new function call, and until it
    is completed, progress on the frame in question comes to a stand-still.

    :param opened_by: The PyagramElement which opened the frame, i.e. the
      :state.program_state.curr_element: in the step immediately preceding that in which the frame
      is instantiated.
    :param frame: The built-in :frame: object wherein live the variable bindings for the function
      call in question.
    """

    def __init__(self, opened_by, frame, *, state=None, is_implicit=False):
        super().__init__(opened_by, state)
        self.is_new_frame = True
        self.is_implicit = is_implicit
        self.initial_bindings = None
        self.bindings = frame.f_locals
        if self.is_global_frame:
            del frame.f_globals['__builtins__']
        else:
            self.function = utils.get_function(frame)
            utils.sort_parameter_bindings(self.bindings, self.function)
            var_positional_index, var_positional_name, var_keyword_name = utils.get_variable_params(self.function)
            self.var_positional_index = var_positional_index
            self.initial_var_pos_args = None if var_positional_name is None else [
                encode.reference_snapshot(positional_argument, self.state.memory_state)
                for positional_argument in self.bindings[var_positional_name]
            ]
            self.initial_var_keyword_args = None if var_keyword_name is None else {
                key: encode.reference_snapshot(value, self.state.memory_state)
                for key, value in self.bindings[var_keyword_name].items()
            }
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
        return 'Global Frame' if self.is_global_frame else f'Frame {self.id}'

    def __str__(self):
        """
        <summary>

        :return:
        """
        return_key = 'return'
        header = f'{repr(self)}' + ('' if self.is_global_frame else f' ({encode.reference_str(self.function)})')
        if self.bindings or self.has_returned:
            key_str_len = display.mapped_len(str)
            val_str_len = display.mapped_len(encode.reference_str)
            max_var_key_len, ret_key_len, max_var_value_len, ret_value_len = 0, 0, 0, 0
            if self.bindings:
                max_var_key_len = key_str_len(max(self.bindings.keys(), key=key_str_len))
                max_var_value_len = val_str_len(max(self.bindings.values(), key=val_str_len))
            if self.has_returned:
                ret_key_len = len(str(return_key))
                ret_value_len = len(encode.reference_str(self.return_value))
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

    def step(self):
        """
        <summary>

        :return:
        """
        # Two goals:
        # (1) Identify all functions floating around in memory, and enforce no two point to the same code object.
        # (2) Obtain a reference to all objects floating around in memory; store said references in the MemoryState.
        objects = list(self.bindings.values())
        if not self.is_global_frame:
            objects.append(self.function)
        if self.has_returned:
            objects.append(self.return_value)
        while objects:
            object = objects.pop()
            if not pyagram_types.is_primitive_type(object):
                self.state.memory_state.track(object)
                if pyagram_types.is_function_type(object):
                    utils.assign_unique_code_object(object)
                    self.state.memory_state.record_parent(self, object)
                    referents = utils.get_defaults(object)
                else:
                    referents = list(gc.get_referents(object))
                objects.extend(
                    referent
                    for referent in referents
                    if not self.state.memory_state.is_tracked(referent)
                )
        # It is desirable that once we draw an object in one step, we will draw that object in every future step even if we lose all references to it. (This is a common confusion with using environment diagrams to understand HOFs; pyagrams will not suffer the same issue.)
        self.is_new_frame = False
        super().step()

    def snapshot(self):
        """
        <summary>

        :return:
        """
        bindings = {
            key: encode.reference_snapshot(value, self.state.memory_state)
            for key, value in self.bindings.items()
        }
        if self.initial_bindings is None:
            self.initial_bindings = bindings
        return {
            'is_curr_element': self is self.state.program_state.curr_element,
            'name': repr(self),
            'parent':
                None
                if self.is_global_frame
                else repr(self.state.memory_state.function_parents[self.function]),
            # 'id': self.id,
            # 'parent_id': 
            #     None
            #     if self.is_global_frame
            #     else self.state.memory_state.function_parents[self.function].id,
            'bindings': bindings,
            'return_value':
                encode.reference_snapshot(self.return_value, self.state.memory_state)
                if self.has_returned
                else None,
            'flags': [flag.snapshot() for flag in self.flags],
        }

    def close(self, return_value):
        """
        <summary>

        :param return_value:
        :return:
        """
        if not self.is_global_frame:
            self.return_value = return_value
            self.has_returned = True
        self.state.step(None)
        self.state.snapshot()
        return self.opened_by
