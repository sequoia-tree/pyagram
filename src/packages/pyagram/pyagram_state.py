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

    def step(self, frame, *step_info, trace_type):
        """
        """
        self.take_snapshot = False
        if self.program_state is None:
            self.program_state = ProgramState(self, frame)
        self.program_state.step(frame, *step_info, trace_type=trace_type)
        self.memory_state.step()
        # ------------------------------------------------------------------------------------------
        # TODO: Only take a snapshot when appropriate!
        # (*) Delete the next line.
        # (*) Set `self.take_snapshot = True` elsewhere in this file (and maybe others).
        # (*) PS: Right now it takes an eternity to run, since you're taking a million snapshots and then filtering out duplicates in postprocess.py.
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
            'print_output': self.print_output.getvalue().split('\n'),
            **self.program_state.snapshot(),
        }
        self.snapshots.append(snapshot)

class ProgramState:
    """
    """

    def __init__(self, state, global_frame):
        self.state = state
        self.global_frame = pyagram_element.PyagramFrame(None, global_frame, state=state)
        self.curr_element = self.global_frame
        self.curr_line_no = 0
        self.exception_info = None
        self.finish_prev_step = None
        self.frame_types = {}
        self.frame_count = 1

    @property
    def is_flag(self):
        """
        """
        return isinstance(self.curr_element, pyagram_element.PyagramFlag)

    @property
    def is_frame(self):
        """
        """
        return isinstance(self.curr_element, pyagram_element.PyagramFrame)

    @property
    def is_ongoing_flag_sans_frame(self):
        """
        """
        return self.is_flag and self.curr_element.frame is None

    @property
    def is_ongoing_frame(self):
        """
        """
        return self.is_frame and not self.curr_element.has_returned

    @property
    def is_complete_flag(self):
        """
        """
        return self.is_flag and self.curr_element.has_returned

    def step(self, frame, *step_info, trace_type):
        """
        """
        if self.finish_prev_step is not None:
            self.finish_prev_step()
            self.finish_prev_step = None
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
            exception_info, = step_info
            _, _, traceback = exception_info
            if traceback.tb_next is None:

                # This is the original exception.

                self.exception_info = exception_info
                self.exception_index = len(self.state.snapshots)
                def finish_prev_step():
                    self.process_exception(frame, frame_type)
                    self.exception_info = None
                self.finish_prev_step = finish_prev_step
            else:
                self.process_exception(frame, frame_type)
        self.global_frame.step()

    def snapshot(self):
        """
        """
        return {
            'global_frame': self.global_frame.snapshot(),
            'curr_line_no': self.curr_line_no,
            'exception': self.state.encoder.encode_exception_info(self.exception_info),
        }

    def process_frame_open(self, frame, frame_type):
        """
        """
        if frame_type is enum.FrameTypes.SRC_CALL:
            is_implicit = self.is_ongoing_frame
            if is_implicit:
                banner = None # TODO: Add support for implicit calls (e.g. calls to magic methods).
                self.open_pyagram_flag(banner)
            self.open_pyagram_frame(frame, is_implicit)
        elif frame_type is enum.FrameTypes.SRC_CALL_PRECURSOR:
            pass
        elif frame_type is enum.FrameTypes.SRC_CALL_SUCCESSOR:
            self.close_pyagram_flag()
        elif frame_type is enum.FrameTypes.CLASS_DEFINITION:
            self.open_class_frame(frame)
        else:
            raise enum.FrameTypes.illegal_enum(frame_type)

    def process_frame_close(self, frame, frame_type, return_value):
        """
        """
        if frame_type is enum.FrameTypes.SRC_CALL:
            self.close_pyagram_frame(return_value)
        elif frame_type is enum.FrameTypes.SRC_CALL_PRECURSOR:
            self.open_pyagram_flag(return_value)
        elif frame_type is enum.FrameTypes.SRC_CALL_SUCCESSOR:
            pass
        elif frame_type is enum.FrameTypes.CLASS_DEFINITION:
            self.close_class_frame(frame)
        else:
            raise enum.FrameTypes.illegal_enum(frame_type)

    def process_exception(self, frame, frame_type):
        """
        """
        while self.is_flag:
            self.curr_element.hidden_from = self.exception_index + 1
            self.curr_element.hide_subflags = True
            self.curr_element = self.curr_element.opened_by

    def open_pyagram_flag(self, banner):
        """
        """
        assert self.is_ongoing_flag_sans_frame or self.is_ongoing_frame
        self.curr_element = self.curr_element.add_flag(banner)

    def open_pyagram_frame(self, frame, is_implicit):
        """
        """
        assert self.is_ongoing_flag_sans_frame
        self.curr_element = self.curr_element.add_frame(frame, is_implicit)

    def open_class_frame(self, frame):
        """
        """
        assert self.is_ongoing_frame
        pyagram_wrapped_object.PyagramClassFrame(frame, state=self.state)

    def close_pyagram_flag(self):
        """
        """
        assert self.is_complete_flag or self.is_ongoing_flag_sans_frame
        self.curr_element = self.curr_element.close()

    def close_pyagram_frame(self, return_value):
        """
        """
        assert self.is_ongoing_frame
        is_implicit = self.curr_element.is_implicit
        pyagram_flag = self.curr_element.close(return_value)
        def finish_prev_step():
            self.curr_element = pyagram_flag
            if is_implicit:
                self.curr_element = self.curr_element.close()
        self.finish_prev_step = finish_prev_step

    def close_class_frame(self, frame):
        """
        """
        assert self.is_ongoing_frame
        def finish_prev_step():
            class_object = frame.f_back.f_locals[frame.f_code.co_name]
            self.state.memory_state.record_class_frame(frame, class_object)
        self.finish_prev_step = finish_prev_step

class MemoryState:
    """
    """

    def __init__(self, state):
        # ------------------------------------------------------------------------------------------
        # TODO: Do you really need ALL these attributes?
        self.state = state
        self.objects = []
        self.object_debuts = {}
        self.wrapped_obj_ids = {}
        self.pg_class_frames = {}
        self.generator_frames = {}
        self.generator_functs = {}
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
                    self.record_parent(curr_frame, object)
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
                    referents = list(inspect.getgeneratorlocals(object).values())
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
            curr_frame.is_new_frame = False

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
        # TODO: Refactor this func
        if object_type is None:
            object_type = enum.ObjectTypes.identify_object_type(object)
        is_object = object_type is not enum.ObjectTypes.PRIMITIVE
        is_unseen = id(object) not in self.object_debuts
        is_masked = id(object) in self.wrapped_obj_ids
        if is_object and is_unseen and not is_masked:
            debut_index = len(self.state.snapshots)
            self.objects.append(object)
            self.object_debuts[id(object)] = debut_index
            if object_type is enum.ObjectTypes.GENERATOR:
                self.generator_functs[object] = utils.get_function(object.gi_frame)

    def record_class_frame(self, frame_object, class_object):
        """
        """
        pyagram_class_frame = self.pg_class_frames[frame_object]
        pyagram_class_frame.wrap_object(class_object)
        pyagram_class_frame.bindings = class_object.__dict__
        pyagram_class_frame.parents = class_object.__bases__

    def record_generator_frame(self, pyagram_frame):
        """
        """
        # TODO: Refactor this func
        generator = None
        for object in gc.get_referrers(pyagram_frame.frame):
            if inspect.isgenerator(object):
                assert generator is None, f'multiple generators refer to frame object {pyagram_frame.frame}'
                generator = object
        assert generator is not None
        if generator in self.generator_frames:
            assert self.generator_frames[generator].frame is pyagram_frame.frame
        self.generator_frames[generator] = pyagram_frame
        self.track(generator, enum.ObjectTypes.GENERATOR)

    def record_parent(self, pyagram_frame, function):
        """
        """
        # TODO: Refactor this func
        if function not in self.function_parents:
            utils.assign_unique_code_object(function)
            if not pyagram_frame.is_global_frame and pyagram_frame.is_new_frame:
                parent = pyagram_frame.opened_by
                while isinstance(parent, pyagram_element.PyagramFlag):
                    parent = parent.opened_by
            else:
                parent = pyagram_frame
            self.function_parents[function] = parent
