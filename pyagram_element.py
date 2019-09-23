import gc
import types

import display
import utils

class PyagramElement:
    """
    <summary>
    """

    def __init__(self, opened_by, program_state):
        self.opened_by = opened_by
        self.program_state = self.opened_by.program_state if program_state is None else program_state
        cls = type(self)
        self.id = cls.COUNT
        cls.COUNT += 1
        self.flags = []

    def step(self):
        """
        <summary>

        :return:
        """
        for flag in self.flags:
            flag.step()

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

    def __init__(self, opened_by, *, program_state=None):
        super().__init__(opened_by, program_state)
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
    
    def step(self):
        """
        <summary>

        :return:
        """
        super().step()
        if self.frame:
            self.frame.step()

    def snapshot(self):
        """
        <summary>

        :return:
        """
        return {
            'is-curr-element': self is self.program_state.curr_element,
            'pyagram-flag': self,
            'frame': None if self.frame is None else self.frame.snapshot(),
            'flags': [flag.snapshot() for flag in self.flags],
        }

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

        frame = PyagramFrame(self, frame, is_implicit=is_implicit)
        self.frame = frame
        return frame

class PyagramFrame(PyagramElement):
    """
    <summary>

    :param opened_by:
    :param frame: the corresponding built-in frame object
    """

    COUNT = 0

    def __init__(self, opened_by, frame, *, program_state=None, is_implicit=False):
        super().__init__(opened_by, program_state)
        self.is_new_frame = True
        self.is_implicit = is_implicit
        self.bindings = frame.f_locals
        if self.is_global_frame:
            del frame.f_globals['__builtins__']
        else:
            self.function = utils.get_function(frame)
            utils.sort_parameter_bindings(self.bindings, self.function)
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
        header = f'{repr(self)}' + ('' if self.is_global_frame else f' ({display.reference_str(self.function)})')
        if self.bindings or self.has_returned:
            key_str_len = utils.mapped_len(str)
            val_str_len = utils.mapped_len(display.reference_str)
            max_var_key_len, ret_key_len, max_var_value_len, ret_value_len = 0, 0, 0, 0
            if self.bindings:
                max_var_key_len = key_str_len(max(self.bindings.keys(), key=key_str_len))
                max_var_value_len = val_str_len(max(self.bindings.values(), key=val_str_len))
            if self.has_returned:
                ret_key_len = len(str(return_key))
                ret_value_len = len(display.reference_str(self.return_value))
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
        # (2) Obtain a reference to all objects floating around in memory; store said references in the ProgramState's memory_state.
        objects = list(self.bindings.values())
        if not self.is_global_frame:
            objects.append(self.function)
        if self.has_returned:
            objects.append(self.return_value)
        while objects:
            object = objects.pop()
            if utils.is_referent_type(object):
                self.program_state.memory_state.track(object)
                if isinstance(object, types.FunctionType):
                    utils.enforce_one_function_per_code_object(object)
                    self.program_state.memory_state.record_parent(self, object)
                    referents = utils.get_defaults(object)
                else:
                    referents = list(gc.get_referents(object))
                objects.extend(
                    referent
                    for referent in referents
                    if not self.program_state.memory_state.is_tracked(referent)
                )
        # It is desirable that once we draw an object in one step, we will draw that object in every future step even if we lose all references to it. (This is a common confusion with using environment diagrams to understand HOFs; pyagrams will not suffer the same issue.)
        self.is_new_frame = False
        super().step()

    def snapshot(self):
        """
        <summary>

        :return:
        """
        return {
            'is-curr-element': self is self.program_state.curr_element,
            'id': self.id,
            'parent-id': 
                None
                if self.is_global_frame
                else self.program_state.memory_state.function_parents[self.function].id,
            'bindings': {
                key: utils.reference_snapshot(value, self.program_state.memory_state)
                for key, value in self.bindings.items()
            },
            'has-returned': self.has_returned,
            'return-value': self.return_value,
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
        return self.opened_by
