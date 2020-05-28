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

    def step(self):
        """
        """
        for flag in self.flags:
            flag.step()

    def add_flag(self, banner_summary, **init_args):
        """
        """
        flag = PyagramFlag(self, banner_summary, **init_args)
        self.flags.append(flag)
        return flag

class PyagramFlag(PyagramElement):
    """
    """

    def __init__(self, opened_by, banner_elements, hidden_snapshot=math.inf, *, state=None):
        super().__init__(opened_by, state)
        # TODO: When you're done refactoring everything, see if you still need the infrastructure for hiding PyagramFlags, and whether you still need to postprocess each PyagramFlag.
        self.banner_elements = [] if banner_elements is None else banner_elements
        self.banner_bindings = []
        self.hidden_snapshot = hidden_snapshot
        self.hide_flags = False
        self.is_builtin = False
        self.frame = None

    @property
    def banner_is_complete(self):
        """
        """
        if len(self.banner_elements) == 0:
            return True
        else:
            _, _, last_binding_idx, _ = self.banner_elements[-1]
            return last_binding_idx < len(self.banner_bindings)

    @property
    def has_returned(self):
        """
        """
        return self.frame is not None and self.frame.has_returned

    @property
    def return_value(self):
        """
        """
        if self.has_returned:
            return self.frame.return_value
        else:
            raise AttributeError(f'PyagramFlag {self} has no return value')

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
        if not self.is_hidden():
            referents = []
            for banner_element in self.banner_elements:
                _, _, binding_idx, unpacking_code = banner_element
                if binding_idx < len(self.banner_bindings):
                    binding = self.banner_bindings[binding_idx]
                    unpacking_type = enum.UnpackingTypes.identify_unpacking_type(unpacking_code)
                    if unpacking_type is enum.UnpackingTypes.NORMAL:
                        referents.append(binding)
                    elif unpacking_type is enum.UnpackingTypes.SINGLY_UNPACKED:
                        for element in [*binding]:
                            referents.append(element)
                    elif unpacking_type is enum.UnpackingTypes.DOUBLY_UNPACKED:
                        for key, value in {**binding}.items():
                            referents.append(key)
                            referents.append(value)
                    else:
                        raise enum.UnpackingTypes.illegal_enum(unpacking_type)
            for referent in referents:
                self.state.memory_state.track(referent)
        if self.frame is not None:
            self.frame.step()
        super().step()

    def fix_init_banner(self):
        """
        """
        assert 0 < len(self.banner_elements)
        _, keyword, binding_idx, unpacking_code = self.banner_elements[0]
        code = '__init__'
        self.banner_elements[0] = (
            code,
            keyword,
            binding_idx,
            unpacking_code,
        )
        self.state.encoder.new_flag_fn_code[self] = code # TODO: Maybe don't keep this in the Encoder?

    def fix_implicit_banner(self, function, bindings):
        """
        """
        def add_banner_element(name, binding_idx, unpacking_code):
            self.banner_elements.append((
                name,
                None,
                binding_idx,
                unpacking_code,
            ))
            return binding_idx + 1
        args = []
        kwds = {}
        for parameter in inspect.signature(function).parameters.values():
            if parameter.kind is inspect.Parameter.POSITIONAL_ONLY:
                args.append(bindings[parameter.name])
            elif parameter.kind is inspect.Parameter.POSITIONAL_OR_KEYWORD:
                args.append(bindings[parameter.name])
            elif parameter.kind is inspect.Parameter.VAR_POSITIONAL:
                args.extend(bindings[parameter.name])
            elif parameter.kind is inspect.Parameter.KEYWORD_ONLY:
                kwds[parameter.name] = bindings[parameter.name]
            elif parameter.kind is inspect.Parameter.VAR_KEYWORD:
                kwds.update(bindings[parameter.name])
            else:
                raise enum.Enum.illegal_enum(parameter.kind)
        num_bindings = 0
        num_bindings = add_banner_element(function.__name__, num_bindings, constants.NORMAL_ARG)
        # TODO: Implicit lambdas, eg in min(..., key=lambda ...), should not appear as "<lambda>". They should appear as the lambda symbol, with the proper subscript.
        if 0 < len(args):
            num_bindings = add_banner_element('...', num_bindings, constants.SINGLY_UNPACKED_ARG)
        if 0 < len(kwds):
            num_bindings = add_banner_element('...', num_bindings, constants.DOUBLY_UNPACKED_ARG)
        self.state.step()
        self.register_callable(function)
        self.state.step()
        if 0 < len(args):
            self.register_argument(args)
            self.state.step()
        if 0 < len(kwds):
            self.register_argument(kwds)
            self.state.step()

    def register_callable(self, callable):
        """
        """
        assert 0 == len(self.banner_bindings)
        if type(callable) is type:
            self.fix_init_banner()
            callable = callable.__init__
        self.banner_bindings.append(callable)
        if enum.ObjectTypes.identify_raw_object_type(callable) not in {
            # TODO: Is a callable user-defined iff it's an ObjectTypes.{FUNCTION, METHOD}?
            # TODO: Ideally there'd be a way to know whether or not it's user-defined ....
            # TODO: Speaking of which, this may fail on some / all imported functions ....
            # TODO: Maybe check that (it's a FUNCTION and __) or (it's a METHOD and ___) ?
            # TODO: Maybe you could make use of the code object's filename or module name?
            enum.ObjectTypes.FUNCTION,
            enum.ObjectTypes.METHOD,
        }:
            self.is_builtin = True

    def register_argument(self, argument):
        """
        """
        assert 0 < len(self.banner_bindings)
        self.banner_bindings.append(argument)

    def add_frame(self, frame, frame_type, **init_args):
        """
        """
        assert self.banner_is_complete
        frame = PyagramFrame(self, frame, frame_type, **init_args)
        self.frame = frame
        return frame

    def close(self):
        """
        """
        if not self.has_returned:
            self.hide_from(0)
            self.hide_flags = True # TODO: This should be an optional arg in the hide_from method.
        return self.opened_by

class PyagramFrame(PyagramElement):
    """
    """

    def __init__(self, opened_by, frame, frame_type, is_implicit=False, *, state=None, function=None, generator=None):
        super().__init__(opened_by, state)
        self.frame = frame
        self.function = function
        self.generator = generator
        if frame_type is None:
            if generator is None:
                frame_type = enum.PyagramFrameTypes.FUNCTION
            else:
                frame_type = enum.PyagramFrameTypes.GENERATOR
        else:
            assert function is None and generator is None
        self.frame_type = frame_type
        self.is_implicit = is_implicit
        if self.is_global_frame:
            del frame.f_globals['__builtins__']
        elif self.is_builtin_frame:
            self.frame_number = self.state.program_state.register_frame()
        elif self.is_function_frame:
            self.frame_number = self.state.program_state.register_frame()
        elif self.is_generator_frame:
            # TODO: This was quite possibly broken by the flag refactor.
            self.state.memory_state.record_generator(self, generator) # TODO: Do you need this?
            self.hide_from(0)
            self.yield_from = None
            self.throws_exc = False
        elif self.is_placeholder_frame:
            pass
        else:
            raise enum.PyagramFrameTypes.illegal_enum(self.frame_type)
        self.has_returned = False
        self.return_value = None

    def __repr__(self):
        """
        """
        if self.is_global_frame:
            return 'Global Frame'
        elif self.is_builtin_frame:
            return f'Frame {self.frame_number}'
        elif self.is_function_frame:
            return f'Frame {self.frame_number}'
        elif self.is_generator_frame:
            return f'Frame {self.state.memory_state.pg_generator_frames[self.generator].number}'
        elif self.is_placeholder_frame:
            return '...'
        else:
            raise enum.PyagramFrameTypes.illegal_enum(self.frame_type)

    @property
    def is_global_frame(self):
        """
        """
        return self.frame_type is enum.PyagramFrameTypes.GLOBAL

    @property
    def is_builtin_frame(self):
        """
        """
        return self.frame_type is enum.PyagramFrameTypes.BUILTIN

    @property
    def is_function_frame(self):
        """
        """
        return self.frame_type is enum.PyagramFrameTypes.FUNCTION

    @property
    def is_generator_frame(self):
        """
        """
        return self.frame_type is enum.PyagramFrameTypes.GENERATOR

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
        elif self.is_builtin_frame:
            return self.state.program_state.global_frame
        elif self.is_function_frame:
            return self.state.memory_state.function_parents[self.function]
        elif self.is_generator_frame:
            return self.state.memory_state.pg_generator_frames[self.generator].parent
        elif self.is_placeholder_frame:
            return None
        else:
            raise enum.PyagramFrameTypes.illegal_enum(self.frame_type)

    @property
    def shows_bindings(self):
        """
        """
        return self.is_global_frame \
            or self.is_function_frame \
            or self.is_generator_frame

    @property
    def shows_return_value(self):
        """
        """
        if self.is_global_frame:
            return False
        elif self.is_builtin_frame:
            return self.has_returned
        elif self.is_function_frame:
            return self.has_returned
        elif self.is_generator_frame:
            return self.has_returned and not self.throws_exc
        elif self.is_placeholder_frame:
            return False
        else:
            raise enum.PyagramFrameTypes.illegal_enum(self.frame_type)

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
        if not self.is_hidden():
            referents = []
            if self.function is not None:
                referents.append(self.function)
            if self.generator is not None:
                referents.append(self.generator)
            if self.shows_bindings:
                self.bindings = self.get_bindings()
                referents.extend(self.bindings.values())
            if self.shows_return_value:
                referents.append(self.return_value)
            for referent in referents:
                self.state.memory_state.track(referent)
        super().step()

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
                self.yield_from = self.generator.gi_yieldfrom
                self.throws_exc = is_gen_exc
            self.has_returned = True
            self.return_value = return_value
        self.state.step()
        return self.opened_by
