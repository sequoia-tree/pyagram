import inspect

from . import constants
from . import utils

class PyagramElement:
    """
    """

    def __init__(self, opened_by, state):
        self.opened_by = opened_by
        self.state = opened_by.state if state is None else state
        self.flags = []

    def step(self):
        """
        """
        for flag in self.flags:
            flag.step()

    def add_flag(self, banner):
        """
        """
        flag = PyagramFlag(self, banner)
        self.flags.append(flag)
        return flag

class PyagramFlag(PyagramElement):
    """
    """

    def __init__(self, opened_by, banner, *, state=None):
        super().__init__(opened_by, state)
        self.is_new_flag = True
        self.is_hidden = False
        banner_elements, banner_bindings = banner
        utils.concatenate_adjacent_strings(banner_elements)
        self.has_processed_subflag_since_prev_eval = False
        self.banner_elements = banner_elements
        self.banner_bindings = banner_bindings
        self.banner_binding_index = 0
        self.positional_arg_index = 0
        self.frame = None

    @property
    def banner_is_complete(self):
        """
        """
        return self.banner_binding_index == len(self.banner_bindings)

    @property
    def has_returned(self):
        """
        """
        return self.frame is not None and self.frame.has_returned

    @property
    def return_value(self):
        """
        """
        assert self.has_returned
        return self.frame.return_value

    def step(self):
        """
        """

        # Fill in every banner binding up to the next one that is obtained through a function call.

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
        if self.frame is not None:
            self.frame.step()
        self.is_new_flag = False
        super().step()

    def snapshot(self):
        """
        """
        # TODO: Still need to refactor this. Double-check / reconsider what you need.
        # TODO: First you'll have to re-think how postprocess.py works.
        return {
            'is_curr_element': self is self.state.program_state.curr_element,
            'pyagram_flag': self,
            'banner_binding_index': self.banner_binding_index,
            'snapshot_index': len(self.state.snapshots),
            'frame': None if self.frame is None or self.is_hidden else self.frame.snapshot(),
            'flags': [
                flag.snapshot()
                for flag in self.flags
            ],
        }

    def evaluate_next_banner_binding(self, expect_call):
        """
        """

        # Examine the next binding.
        # If it turns out to be a call:
        # (*) DON'T evaluate it.
        # (*) Return False.
        # Else:
        # (*) Evaluate the binding.
        # (*) Return True.
        # Return False if the banner gets completed.

        binding = self.banner_bindings[self.banner_binding_index]
        is_unsupported_binding = binding is None
        if is_unsupported_binding:
            self.state.snapshot()
            while not self.banner_is_complete:
                self.banner_bindings[self.banner_binding_index] = constants.BANNER_UNSUPPORTED_CODE
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
                        self.banner_bindings[self.banner_binding_index] = constants.BANNER_FUNCTION_CODE
                    else:
                        self.banner_bindings[self.banner_binding_index] = self.positional_arg_index
                        self.positional_arg_index += 1
                else:
                    self.banner_bindings[self.banner_binding_index] = param_if_known
                self.banner_binding_index += 1
                return True

    def add_frame(self, frame, is_implicit):
        """
        """
        assert self.banner_is_complete
        frame = PyagramFrame(self, frame, is_implicit)
        self.frame = frame
        return frame

    def close(self):
        """
        """
        if self.frame is None:
            self.is_hidden = True
        return self.opened_by

class PyagramFrame(PyagramElement):
    """
    """

    def __init__(self, opened_by, frame, is_implicit=False, *, state=None):
        super().__init__(opened_by, state)
        self.is_new_frame = True
        self.is_implicit = is_implicit
        self.frame = frame
        self.initial_bindings = None
        if self.is_global_frame:
            del frame.f_globals['__builtins__']
        else:
            self.function = utils.get_function(frame)
            self.state.memory_state.record_parent(self, self.function)
            if utils.is_generator_frame(self):
                self.opened_by.is_hidden = True
                self.state.memory_state.record_generator_frame(self)
            else:
                var_positional_index, var_positional_name, var_keyword_name = utils.get_variable_params(self.function)
                self.var_positional_index = var_positional_index
                self.initial_var_pos_args = None if var_positional_name is None else [
                    self.state.encoder.reference_snapshot(positional_argument)
                    for positional_argument in self.frame.f_locals[var_positional_name]
                ]
                self.initial_var_keyword_args = None if var_keyword_name is None else {
                    key: self.state.encoder.reference_snapshot(value)
                    for key, value in self.frame.f_locals[var_keyword_name].items()
                }
                self.frame_number = self.state.program_state.frame_count
                self.state.program_state.frame_count += 1
        self.has_returned = False
        self.return_value = None

    @property
    def is_global_frame(self):
        """
        """
        return self.opened_by is None

    @property
    def parent(self):
        """
        """
        return None if self.is_global_frame else self.state.memory_state.function_parents[self.function]

    def __repr__(self):
        """
        """
        return 'Global Frame' if self.is_global_frame else f'Frame {self.frame_number}'

    def step(self):
        """
        """
        self.bindings = self.get_bindings()
        referents = list(self.bindings.values())
        if not self.is_global_frame:
            referents.append(self.function)
        if self.has_returned:
            referents.append(self.return_value)
        for referent in referents:
            self.state.memory_state.track(referent)
        super().step()

    def snapshot(self):
        """
        """
        bindings = {
            key: self.state.encoder.reference_snapshot(value)
            for key, value in self.bindings.items()
        }
        if self.initial_bindings is None:
            self.initial_bindings = bindings
        # TODO: Still need to refactor this. Double-check / reconsider what you need.
        # TODO: First you'll have to re-think how postprocess.py works.
        return {
            'is_curr_element': self is self.state.program_state.curr_element,
            'name': repr(self),
            'parents':
                []
                if self.parent is None
                else [repr(self.parent)],
            'bindings': bindings,
            'return_value':
                self.state.encoder.reference_snapshot(self.return_value)
                if self.has_returned
                else None,
            'flags': [
                flag.snapshot()
                for flag in self.flags
            ],
        }

    def get_bindings(self):
        """
        """
        sorted_binding_names = [] if self.is_global_frame else list(
            inspect.signature(self.function).parameters.keys(),
        )
        for variable, value in self.frame.f_locals.items():
            is_in_parent_frame = False
            next_frame_to_scan = self.parent
            while next_frame_to_scan is not None:
                if variable in next_frame_to_scan.frame.f_locals and next_frame_to_scan.frame.f_locals[variable] == value:
                    is_in_parent_frame = True
                    break
                next_frame_to_scan = next_frame_to_scan.parent
            if variable in self.frame.f_code.co_varnames or not is_in_parent_frame:
                sorted_binding_names.append(variable)
        return {
            variable: self.frame.f_locals[variable]
            for variable in sorted_binding_names
        }

    def close(self, return_value):
        """
        """
        if not self.is_global_frame:
            self.has_returned = True
            self.return_value = return_value
        return self.opened_by
