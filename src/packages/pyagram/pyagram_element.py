import inspect
import math

from . import constants
from . import enum
from . import utils

class PyagramElement:
    """
    """

    def __init__(self, opened_by, state):
        self.opened_by = opened_by
        self.state = opened_by.state if state is None else state
        self.flags = []
        self.is_new = True

    def step(self):
        """
        """
        for flag in self.flags:
            flag.step()

    def add_flag(self, banner, **init_args):
        """
        """
        flag = PyagramFlag(self, banner, **init_args)
        self.flags.append(flag)
        return flag

class PyagramFlag(PyagramElement):
    """
    """

    def __init__(self, opened_by, banner, hidden_snapshot=math.inf, *, state=None):
        super().__init__(opened_by, state)
        if banner is None:
            banner_elements, banner_bindings = [], []
        else:
            banner_elements, banner_bindings = banner
            utils.concatenate_adjacent_strings(banner_elements)
        self.hidden_snapshot = hidden_snapshot
        self.hidden_subflags = False
        self.banner_elements = banner_elements
        self.banner_bindings = banner_bindings
        self.banner_binding_index = 0
        self.positional_arg_index = 0
        self.has_processed_subflag_since_prev_eval = False
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

    def hide_from(self, snapshot_index):
        """
        """
        self.hidden_snapshot = min(self.hidden_snapshot, snapshot_index)

    def is_hidden(self, snapshot_index=None):
        """
        """
        if snapshot_index is None:
            snapshot_index = len(self.state.snapshots)
        return self.hidden_snapshot <= snapshot_index

    def step(self):
        """
        """

        # Fill in every banner binding up to the next one that is obtained through a function call.

        if not self.banner_is_complete:
            if self is self.state.program_state.curr_element:
                if self.is_new or self.has_processed_subflag_since_prev_eval:
                    self.evaluate_next_banner_bindings()
                self.has_processed_subflag_since_prev_eval = False
            else:
                self.has_processed_subflag_since_prev_eval = True
        if self.frame is not None:
            self.frame.step()
        self.is_new = False
        super().step()

    def snapshot(self):
        """
        """
        is_hidden = self.is_hidden()
        return {
            'is_curr_element': self is self.state.program_state.curr_element,
            'banner': None, # Placeholder.
            'frame':
                None
                if self.frame is None or is_hidden
                else self.frame.snapshot(),
            'flags':
                []
                if self.hidden_subflags
                else [
                    flag.snapshot()
                    for flag in self.flags + (
                        self.frame.flags
                        if is_hidden and self.frame is not None
                        else []
                    )
                ],
            'self': self, # For postprocessing.
            'banner_binding_index': self.banner_binding_index, # For postprocessing.
            'snapshot_index': len(self.state.snapshots), # For postprocessing.
        }

    def evaluate_next_banner_bindings(self, *, skip_args=False):
        """
        """
        self.state.snapshot()
        if not self.is_new:
            assert not skip_args
            self.evaluate_next_banner_binding(True)
        next_binding_might_not_be_call = True
        while next_binding_might_not_be_call and not self.banner_is_complete:
            next_binding_might_not_be_call = self.evaluate_next_banner_binding(
                False,
                skip_args=skip_args,
            )

    def evaluate_next_banner_binding(self, expect_call, *, skip_args=False):
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
            while not self.banner_is_complete:
                self.banner_bindings[self.banner_binding_index] = constants.BANNER_UNSUPPORTED_CODE
                self.banner_binding_index += 1
            self.state.snapshot()
            return False
        else:
            is_call, param_if_known = binding
            if is_call and not expect_call:
                return False
            else:
                is_func_binding = self.banner_binding_index == 0
                if param_if_known is None:
                    if is_func_binding:
                        self.banner_bindings[self.banner_binding_index] = constants.BANNER_FUNCTION_CODE
                    else:
                        self.banner_bindings[self.banner_binding_index] = self.positional_arg_index
                        self.positional_arg_index += 1
                else:
                    assert not is_func_binding
                    self.banner_bindings[self.banner_binding_index] = param_if_known
                self.banner_binding_index += 1
                if not skip_args or is_func_binding or self.banner_is_complete:
                    self.state.snapshot()
                return True

    def add_frame(self, frame, **init_args):
        """
        """
        assert self.banner_is_complete
        frame = PyagramFrame(self, frame, **init_args)
        self.frame = frame
        return frame

    def close(self):
        """
        """
        if self.frame is None:
            self.hide_from(0)
        return self.opened_by

class PyagramFrame(PyagramElement):
    """
    """

    def __init__(self, opened_by, frame, is_implicit=False, is_placeholder=False, *, state=None):
        super().__init__(opened_by, state)
        self.frame = frame
        self.function = None if is_placeholder else utils.get_function(frame)
        self.generator = None if is_placeholder else utils.get_generator(frame)
        self.frame_type = enum.PyagramFrameTypes.identify_pyagram_frame_type(self)
        self.is_implicit = is_implicit
        if self.is_global_frame:
            del frame.f_globals['__builtins__']
        elif self.is_generator_frame:
            self.state.memory_state.record_generator(self, self.generator)
            self.hide_from(0)
            self.throws_exc = False
        elif self.is_function_frame:
            self.state.memory_state.record_function(self, self.function)
            self.frame_number = self.state.program_state.register_frame()
            utils.fix_init_banner(opened_by.banner_elements, self.function)
            var_positional_index, var_positional_name, var_keyword_name = utils.get_variable_params(self.function)
            self.var_positional_index = var_positional_index
            self.initial_var_pos_args = None if var_positional_name is None else [
                self.state.encoder.reference_snapshot(positional_argument)
                for positional_argument in frame.f_locals[var_positional_name]
            ]
            self.initial_var_keyword_args = None if var_keyword_name is None else {
                key: self.state.encoder.reference_snapshot(value)
                for key, value in frame.f_locals[var_keyword_name].items()
            }
            self.initial_bindings = {
                key: self.state.encoder.reference_snapshot(value)
                for key, value in self.get_bindings().items()
            }
            if is_implicit:
                flag = opened_by
                num_args = len(self.initial_bindings)
                num_bindings = 1 + num_args
                flag.banner_elements = [
                    (
                        self.function.__name__,
                        [0],
                    ),
                    '(',
                    (
                        '...',
                        list(range(1, num_bindings)),
                    ),
                    ')',
                ]
                flag.banner_bindings = [(False, None)] * num_bindings
                flag.evaluate_next_banner_bindings(skip_args=True)
        elif self.is_placeholder_frame:
            pass
        else:
            raise enum.PyagramFrameTypes.illegal_enum(self.frame_type)
        self.has_returned = False
        self.return_value = None

    def __repr__(self):
        """
        """
        if self.frame_type is enum.PyagramFrameTypes.GLOBAL:
            return 'Global Frame'
        elif self.frame_type is enum.PyagramFrameTypes.GENERATOR:
            return f'Frame {self.state.memory_state.generator_numbers[self.generator]}'
        elif self.frame_type is enum.PyagramFrameTypes.FUNCTION:
            return f'Frame {self.frame_number}'
        elif self.frame_type is enum.PyagramFrameTypes.PLACEHOLDER:
            return ''
        else:
            raise enum.PyagramFrameTypes.illegal_enum(self.frame_type)

    @property
    def is_global_frame(self):
        """
        """
        return self.frame_type is enum.PyagramFrameTypes.GLOBAL

    @property
    def is_generator_frame(self):
        """
        """
        return self.frame_type is enum.PyagramFrameTypes.GENERATOR

    @property
    def is_function_frame(self):
        """
        """
        return self.frame_type is enum.PyagramFrameTypes.FUNCTION

    @property
    def is_placeholder_frame(self):
        """
        """
        return self.frame_type is enum.PyagramFrameTypes.PLACEHOLDER

    @property
    def parent(self):
        """
        """
        if self.is_global_frame:
            return None
        elif self.is_generator_frame:
            return self.state.memory_state.generator_parents[self.generator]
        elif self.is_function_frame:
            return self.state.memory_state.function_parents[self.function]
        elif self.is_placeholder_frame:
            return None
        else:
            raise enum.PyagramFrameTypes.illegal_enum(self.frame_type)

    @property
    def shows_return_value(self):
        """
        """
        return self.has_returned and not (self.is_generator_frame and self.throws_exc)

    def hide_from(self, snapshot_index):
        """
        """
        if self.opened_by is not None:
            self.opened_by.hide_from(snapshot_index)

    def is_hidden(self, snapshot_index=None):
        """
        """
        return self.opened_by is not None and self.opened_by.is_hidden(snapshot_index)

    def step(self):
        """
        """
        if self.frame_type is not enum.PyagramFrameTypes.PLACEHOLDER:
            self.bindings = self.get_bindings()
            if not self.is_hidden():
                referents = list(self.bindings.values())
                if self.function is not None:
                    referents.append(self.function)
                if self.generator is not None:
                    referents.append(self.generator)
                if self.shows_return_value:
                    referents.append(self.return_value)
                for referent in referents:
                    self.state.memory_state.track(referent)
        super().step()

    def snapshot(self):
        """
        """
        return {
            'type': 'function',
            'is_curr_element': self is self.state.program_state.curr_element,
            'name': repr(self),
            'parent':
                None
                if self.parent is None
                else repr(self.parent),
            'bindings': self.state.encoder.encode_mapping(
                self.bindings,
                is_bindings=True,
            ),
            'return_value':
                self.state.encoder.reference_snapshot(self.return_value)
                if self.shows_return_value
                else None,
            'from': None,
            'flags': [
                flag.snapshot()
                for flag in self.flags
            ],
        }

    def get_bindings(self):
        """
        """
        sorted_binding_names = [] if self.function is None else list(
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

    def close(self, return_value, *, is_gen_exc=False):
        """
        """
        if not self.is_global_frame:
            if self.is_generator_frame:
                self.throws_exc = is_gen_exc
            self.has_returned = True
            self.return_value = return_value
        self.state.step()
        return self.opened_by
