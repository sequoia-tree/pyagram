import gc
import inspect

from . import encode
from . import enum
from . import pyagram_element
from . import pyagram_wrapped_object
from . import utils

class State:
    """
    """

    def __init__(self, preprocessor_summary, stdout):
        self.program_state = None
        self.memory_state = MemoryState(self)
        self.print_output = stdout
        self.encoder = encode.Encoder(self, preprocessor_summary)
        self.snapshots = []

    def step(self, *args):
        """
        """
        if 0 == len(args):
            self.take_snapshot = True
        else:
            self.take_snapshot = False
            if self.program_state is None:
                frame, *_ = args
                self.program_state = ProgramState(self, frame)
            self.program_state.process_trace_event(*args)
        self.program_state.step()
        self.memory_state.step()
        # ------------------------------------------------------------------------------------------
        # TODO: Only take a snapshot when appropriate!
        # (*) Delete the next line.
        # (*) Set `self.take_snapshot = True` elsewhere in this file (and maybe others).
        # (*) PS: Right now it takes an eternity to run, since you're taking a million snapshots and then filtering out duplicates in postprocess.py.
        # (*) Don't take the last snapshot where curr_elem is None.
        self.take_snapshot = True
        # TODO: Before working on this bit, or comment out kill_static_snapshots in postprocess.py.
        # ------------------------------------------------------------------------------------------
        if self.take_snapshot:
            self.snapshot()

    def snapshot(self):
        """
        """
        snapshot = {
            'memory_state': self.memory_state.snapshot(),
            'print_output': self.print_output.getvalue(),
            **self.program_state.snapshot(),
        }
        self.snapshots.append(snapshot)

class ProgramState:
    """
    """

    def __init__(self, state, global_frame):
        self.state = state
        self.global_frame = pyagram_element.PyagramFrame(
            None,
            global_frame,
            enum.PyagramFrameTypes.GLOBAL,
            state=state,
        )
        self.curr_element = self.global_frame
        self.curr_line_no = 0
        self.prev_trace_type = None
        self.curr_trace_type = None
        self.caught_exc_info = None
        self.finish_prev = None
        self.frame_types = {}
        self.frame_count = 0

    @property
    def is_flag(self):
        """
        """
        return isinstance(self.curr_element, pyagram_element.PyagramFlag)

    @property
    def is_ongoing_flag_sans_frame(self):
        """
        """
        return self.is_flag and self.curr_element.frame is None

    @property
    def is_ongoing_flag_with_frame(self):
        """
        """
        return self.is_flag and self.curr_element.frame is not None

    @property
    def is_complete_flag(self):
        """
        """
        return self.is_flag and self.curr_element.has_returned

    @property
    def is_frame(self):
        """
        """
        return isinstance(self.curr_element, pyagram_element.PyagramFrame)

    @property
    def is_ongoing_frame(self):
        """
        """
        return self.is_frame and not self.curr_element.has_returned

    @property
    def is_complete_frame(self):
        """
        """
        return self.is_frame and self.curr_element.has_returned

    def step(self):
        """
        """
        self.global_frame.step()

    def snapshot(self):
        """
        """
        return {
            'global_frame': self.state.encoder.encode_pyagram_frame(self.global_frame),
            'curr_line_no': self.curr_line_no,
            'exception': self.state.encoder.encode_caught_exc_info(self.caught_exc_info),
        }

    def process_trace_event(self, frame, trace_type, *step_info):
        """
        """
        self.curr_trace_type = trace_type
        if self.finish_prev is not None:
            self.finish_prev()
            self.finish_prev = None
        line_no, step_code, _ = utils.decode_lineno(
            frame.f_lineno,
            max_lineno=self.state.encoder.num_lines,
        )
        self.curr_line_no = line_no
        if frame not in self.frame_types:
            self.frame_types[frame] = enum.FrameTypes.identify_frame_type(step_code)
        frame_type = self.frame_types[frame]
        if trace_type is enum.TraceTypes.USER_CALL:
            self.process_frame_open(frame, frame_type)
        elif trace_type is enum.TraceTypes.USER_LINE:
            pass
        elif trace_type is enum.TraceTypes.USER_RETURN:
            return_value, = step_info
            self.process_frame_close(frame, frame_type, return_value)
        elif trace_type is enum.TraceTypes.USER_EXCEPTION:
            caught_exc_info, = step_info
            self.process_exception(frame, frame_type, caught_exc_info)
        self.prev_trace_type = trace_type

    def process_frame_open(self, frame, frame_type):
        """
        """
        if frame_type is enum.FrameTypes.SRC_CALL:
            is_implicit = self.is_ongoing_frame
            if is_implicit:
                self.open_pyagram_flag(frame, None)
            self.open_pyagram_frame(frame, None, is_implicit=is_implicit)
        elif frame_type is enum.FrameTypes.SRC_CALL_FN_WRAPPER:
            pass
        elif frame_type is enum.FrameTypes.SRC_CALL_RG_WRAPPER:
            pass
        elif frame_type is enum.FrameTypes.SRC_CALL_PRECURSOR:
            pass
        elif frame_type is enum.FrameTypes.SRC_CALL_SUCCESSOR:
            pass
        elif frame_type is enum.FrameTypes.CLASS_DEFINITION:
            self.open_class_frame(frame)
        elif frame_type is enum.FrameTypes.COMPREHENSION:
            self.open_comprehension(frame)
        else:
            raise enum.FrameTypes.illegal_enum(frame_type)

    def process_frame_close(self, frame, frame_type, return_value):
        """
        """
        if frame_type is enum.FrameTypes.SRC_CALL:
            self.close_pyagram_frame(frame, return_value)
        elif frame_type is enum.FrameTypes.SRC_CALL_FN_WRAPPER:
            self.register_callable(frame, return_value)
        elif frame_type is enum.FrameTypes.SRC_CALL_RG_WRAPPER:
            self.register_argument(frame, return_value)
        elif frame_type is enum.FrameTypes.SRC_CALL_PRECURSOR:
            self.open_pyagram_flag(frame, return_value)
        elif frame_type is enum.FrameTypes.SRC_CALL_SUCCESSOR:
            if self.curr_element is not self.global_frame: # TODO: This is sloppy.
                self.close_pyagram_flag(frame, return_value)
        elif frame_type is enum.FrameTypes.CLASS_DEFINITION:
            self.close_class_frame(frame, return_value)
        elif frame_type is enum.FrameTypes.COMPREHENSION:
            self.close_comprehension(frame, return_value)
        else:
            raise enum.FrameTypes.illegal_enum(frame_type)

    def process_exception(self, frame, frame_type, caught_exc_info):
        """
        """
        _, _, traceback = caught_exc_info
        if traceback.tb_next is None:

            # This is the original exception.

            self.caught_exc_info = caught_exc_info
            self.exception_index = len(self.state.snapshots)
            is_placeholder_exception = self.is_frame \
                and self.curr_element.is_placeholder_frame
            is_generator_exception = self.is_flag \
                and self.curr_element.frame is not None \
                and self.curr_element.frame.is_generator_frame
            if is_placeholder_exception:
                exception_element = self.curr_element
                self.curr_element = self.curr_element.opened_by.opened_by
            if is_generator_exception:
                exception_element = self.curr_element
                self.curr_element = self.curr_element.frame
            def finish_step():
                if is_placeholder_exception or is_generator_exception:
                    self.curr_element = exception_element
                self.process_traceback(frame, frame_type)
                self.caught_exc_info = None
            self.defer(finish_step)
        else:
            self.process_traceback(frame, frame_type)

    def process_traceback(self, frame, frame_type):
        """
        """
        if self.is_frame:
            self.curr_element.hide_from(self.exception_index + 1)
        while self.is_flag:
            self.curr_element.hide_from(self.exception_index + 1)
            self.curr_element.hidden_subflags = True
            self.curr_element = self.curr_element.opened_by

    def open_pyagram_flag(self, frame, banner_summary, **init_args):
        """
        """
        assert self.is_ongoing_flag_sans_frame or self.is_ongoing_frame
        self.curr_element = self.curr_element.add_flag(banner_summary, **init_args)

    def open_pyagram_frame(self, frame, frame_type, **init_args):
        """
        """
        assert self.is_ongoing_flag_sans_frame
        self.curr_element = self.curr_element.add_frame(frame, frame_type, **init_args)

    def open_class_frame(self, frame):
        """
        """
        assert self.is_ongoing_frame
        pyagram_wrapped_object.PyagramClassFrame(frame, state=self.state)

    def open_comprehension(self, frame):
        """
        """
        # TODO: Revisit comprehension logic after the refactor.
        assert self.is_ongoing_flag_sans_frame or self.is_ongoing_frame
        self.open_pyagram_flag(frame, None, hidden_snapshot=0)
        self.open_pyagram_frame(frame, enum.PyagramFrameTypes.PLACEHOLDER)

    def close_pyagram_flag(self, frame, return_value):
        """
        """
        assert self.is_flag
        if self.curr_element.is_builtin:

            self.open_pyagram_frame(frame, enum.PyagramFrameTypes.BUILTIN)
            # TODO: Take a snapshot (no need to step first) after opening the frame, so the return value doesn't immediately appear.
            self.close_pyagram_frame(frame, None)
            # TODO: Make sure to track the return value! Right now it doesn't.

        assert self.is_complete_flag
        self.curr_element = self.curr_element.close()

    def close_pyagram_frame(self, frame, return_value):
        """
        """
        assert self.is_ongoing_frame
        def finish_step():
            is_implicit = self.curr_element.is_implicit
            self.curr_element = self.curr_element.close(
                return_value,
                is_gen_exc=self.curr_trace_type is enum.TraceTypes.USER_EXCEPTION,
            )
            if is_implicit:
                self.curr_element = self.curr_element.close()
        if self.curr_element.is_global_frame:
            pass
        elif self.curr_element.is_builtin_frame:
            finish_step()
        elif self.curr_element.is_function_frame:
            finish_step()
        elif self.curr_element.is_generator_frame:
            self.defer(finish_step)
        elif self.curr_element.is_placeholder_frame:
            finish_step()
        else:
            raise enum.PyagramFrameTypes.illegal_enum(self.curr_element.frame_type)

    def close_class_frame(self, frame, return_value):
        """
        """
        assert self.is_ongoing_frame
        def finish_step():
            parent_bindings, class_name = frame.f_back.f_locals, frame.f_code.co_name
            if class_name in parent_bindings:
                self.state.memory_state.record_class_frame(frame, parent_bindings[class_name])
        self.defer(finish_step)

    def close_comprehension(self, frame, return_value):
        """
        """
        # TODO: Revisit comprehension logic after the refactor.
        raises_error = self.prev_trace_type is enum.TraceTypes.USER_EXCEPTION
        if return_value is None and not raises_error:
            return
        assert self.is_ongoing_frame
        self.close_pyagram_frame(frame, return_value)
        self.close_pyagram_flag(frame, None)
        # TODO: This is definitely broken now.

    def register_callable(self, frame, callable):
        """
        """
        assert self.is_ongoing_flag_sans_frame and 0 == len(self.curr_element.banner_bindings)
        if type(callable) is type:
            self.curr_element.fix_obj_instantiation_banner()
            callable = callable.__init__
            # TODO: Make it work nicely for when the __init__ isn't user-defined (see the todo in PyagramFlag.step).
            # TODO: I think you should test whether the callable is tracked already (or maybe whether it's a method, rather than a slot wrapper or method descriptor). If so, then proceed as normal. Otherwise, close the flag and hide it. (You should NOT display a flag for the instantiation of an object that has no user-defined __init__ method. That would get SO annoying.)
        if enum.ObjectTypes.identify_object_type(callable) is enum.ObjectTypes.BUILTIN:

            # Make sure this is triggered by EVERY callable that doesn't expose a frame to us.

            self.curr_element.is_builtin = True

            # TODO: Actually, don't open the frame here. Instead, just mark the flag as a builtin
            # TODO: flag and give it the function. Then, before ...
            # TODO:       (1) opening an implicit frame, or ...
            # TODO:       (2) closing a flag ...
            # TODO: ... check if the curr_element is a builtin flag. If so, Add the placeholder
            # TODO: builtin frame, take a snapshot, close the placeholder frame, and continue.

            # TODO: To get the return value for the builtin frame, you can get it in the SRC_CALL_SUCCESSOR's close event.

            # self.open_pyagram_frame(frame, enum.PyagramFrameTypes.BUILTIN)
        else:
            pass # TODO
            # TODO: Do self.curr_element.function = function. Atm PyagramFlag.function is unused.
            # TODO: You may be able to avoid the necessity of giving each func a unique code object.
        self.curr_element.banner_bindings.append(callable) # TODO: Give the PyagramFlag a method (set_func) for this, and a method (set_arg or set_binding) for below.

    def register_argument(self, frame, return_value):
        """
        """
        assert self.is_ongoing_flag_sans_frame and 0 < len(self.curr_element.banner_bindings)
        self.curr_element.banner_bindings.append(return_value)

    def register_frame(self):
        """
        """
        self.frame_count += 1
        return self.frame_count

    def defer(self, function):
        """
        """
        assert self.finish_prev is None
        self.finish_prev = function

class MemoryState:
    """
    """

    def __init__(self, state):
        # ------------------------------------------------------------------------------------------
        # TODO: Do you really need ALL these attributes?
        self.state = state
        self.objects = []
        self.tracked_obj_ids = set()
        self.wrapped_obj_ids = {}
        self.pg_class_frames = {}
        self.latest_gen_frames = {} # TODO: Maybe combine these 3 dicts into a class or namedtuple?
        self.generator_numbers = {} # TODO: You should combine gen_numbers and gen_parents into one.
        self.generator_parents = {}
        self.function_parents = {}
        # ------------------------------------------------------------------------------------------

    def step(self):
        """
        """
        if isinstance(self.state.program_state.curr_element, pyagram_element.PyagramFrame):
            curr_frame = self.state.program_state.curr_element
            for object in self.objects:
                object_type = enum.ObjectTypes.identify_object_type(object)
                if object_type is enum.ObjectTypes.PRIMITIVE:
                    referents = []
                elif object_type is enum.ObjectTypes.FUNCTION:
                    self.record_function(curr_frame, object)
                    referents = utils.get_defaults(object)
                elif object_type is enum.ObjectTypes.BUILTIN:
                    referents = []
                elif object_type is enum.ObjectTypes.ORDERED_COLLECTION:
                    referents = list(object)
                elif object_type is enum.ObjectTypes.UNORDERED_COLLECTION:
                    referents = list(object)
                elif object_type is enum.ObjectTypes.MAPPING:
                    keys, values = list(object.keys()), list(object.values())
                    referents = keys
                    referents.extend(values)
                elif object_type is enum.ObjectTypes.ITERATOR:
                    iterable = utils.get_iterable(object)
                    referents = [] if iterable is None else [iterable]
                elif object_type is enum.ObjectTypes.GENERATOR:
                    referents = [
                        value
                        for variable, value in inspect.getgeneratorlocals(object).items()
                        if utils.is_genuine_binding(variable)
                    ]
                    if object in self.latest_gen_frames and self.latest_gen_frames[object].shows_return_value:
                        referents.append(self.latest_gen_frames[object].return_value)
                    if object.gi_yieldfrom is not None:
                        referents.append(object.gi_yieldfrom)
                elif object_type is enum.ObjectTypes.OBJ_CLASS:
                    referents = [
                        value
                        for key, value in object.bindings.items()
                        if key not in pyagram_wrapped_object.PyagramClassFrame.HIDDEN_BINDINGS
                    ]
                elif object_type is enum.ObjectTypes.OBJ_INST:
                    referents = object.__dict__.values()
                elif object_type is enum.ObjectTypes.OTHER:
                    referents = []
                else:
                    raise enum.ObjectTypes.illegal_enum(object_type)
                for referent in referents:
                    self.track(referent)
            curr_frame.is_new = False

    def snapshot(self):
        """
        """
        return [
            {
                'id': id(object),
                'object': self.state.encoder.object_snapshot(object),
            }
            for object in self.objects
        ]

    def track(self, object, object_type=None):
        """
        """
        if object_type is None:
            object_type = enum.ObjectTypes.identify_object_type(object)
        is_object = object_type is not enum.ObjectTypes.PRIMITIVE
        is_unseen = id(object) not in self.tracked_obj_ids
        is_masked = id(object) in self.wrapped_obj_ids
        if is_object and is_unseen and not is_masked:
            self.objects.append(object)
            self.tracked_obj_ids.add(id(object))
            if object_type is enum.ObjectTypes.GENERATOR:
                generator_function = utils.get_function(object.gi_frame)
                if generator_function is None:
                    parent = self.state.program_state.curr_element
                else:
                    parent = self.function_parents[generator_function]
                self.generator_numbers[object] = self.state.program_state.register_frame()
                self.generator_parents[object] = parent

    def record_class_frame(self, frame_object, class_object):
        """
        """
        pyagram_class_frame = self.pg_class_frames[frame_object]
        pyagram_class_frame.wrap_object(class_object)
        pyagram_class_frame.bindings = class_object.__dict__
        pyagram_class_frame.parents = class_object.__bases__

    def record_generator(self, pyagram_frame, generator):
        """
        """
        self.latest_gen_frames[generator] = pyagram_frame
        self.track(generator, enum.ObjectTypes.GENERATOR)

    def record_function(self, pyagram_frame, function):
        """
        """
        if function not in self.function_parents:
            utils.assign_unique_code_object(function)
            if pyagram_frame.is_new and pyagram_frame.opened_by is not None:
                parent = pyagram_frame.opened_by
                while isinstance(parent, pyagram_element.PyagramFlag):
                    parent = parent.opened_by
            else:
                parent = pyagram_frame
            self.function_parents[function] = parent
        self.track(function, enum.ObjectTypes.FUNCTION)
