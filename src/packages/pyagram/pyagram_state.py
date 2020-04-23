import gc
import inspect

from . import encode
from . import enum
from . import pyagram_element
from . import pyagram_types
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
        # ------------------------------------------------------------------------------------------
        # TODO: Do this differently? Might be incorrect w generators, classes, built-ins, or hidden frames ...
        self.num_pyagram_flags, self.num_pyagram_frames = 0, 0
        # ------------------------------------------------------------------------------------------

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
        # ------------------------------------------------------------------------------------------
        if self.take_snapshot:
            self.snapshot()

    def snapshot(self):
        """
        """
        # TODO: Rearrange the snapshots for better congruency with the `render` module.
        # TODO: Also, consider serializing like `snapshot = [x, y, z]` instead of `snapshot = {'x': x, 'y': y, 'z': z}`. It would be more space-efficient and it'd be really nice to be able to write `x, y, z = snapshot` (or, in JS, `var [x, y, z] = snapshot`).
        # TODO: The curr_line_no should be in the State's snapshot, while the ProgramState's snapshot should just `return self.global_frame.snapshot()`.
        snapshot = {
            'program_state': self.program_state.snapshot(),
            'memory_state': self.memory_state.snapshot(),
            'print_output': self.print_output.getvalue().split('\n'),
        }
        self.snapshots.append(snapshot)

class ProgramState:
    """
    """

    def __init__(self, state, global_frame):
        self.state = state
        self.global_frame = pyagram_element.PyagramFrame(None, global_frame, state=state) # TODO: Change signature?
        self.curr_element = self.global_frame
        self.curr_line_no = 0
        self.finish_prev_step = None
        self.frame_types = {}

    @property
    def is_ongoing_flag_sans_frame(self):
        """
        """
        is_flag = isinstance(self.curr_element, pyagram_element.PyagramFlag)
        return is_flag and self.curr_element.frame is None

    @property
    def is_ongoing_frame(self):
        """
        """
        is_frame = isinstance(self.curr_element, pyagram_element.PyagramFrame)
        return is_frame and not self.curr_element.has_returned

    @property
    def is_complete_flag(self):
        """
        """
        is_flag = isinstance(self.curr_element, pyagram_element.PyagramFlag)
        return is_flag and self.curr_element.has_returned

    def step(self, frame, *step_info, trace_type):
        """
        """
        if self.finish_prev_step is not None:
            self.finish_prev_step()
            self.finish_prev_step = None
        line_no, step_code, lambda_number = utils.decode_lineno(
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
            pass
        self.global_frame.step()

    def snapshot(self):
        """
        """
        return {
            'global_frame': self.global_frame.snapshot(),
            'curr_line_no': self.curr_line_no,
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
        class_frame = pyagram_wrapped_object.PyagramClassFrame(frame, state=self.state) # TODO: Change signature?
        self.state.memory_state.track(class_frame)

    def close_pyagram_flag(self):
        """
        """
        assert self.is_complete_flag or self.is_ongoing_flag_sans_frame
        if self.is_ongoing_flag_sans_frame:

            # If we call a built-in function, we open a flag but bdb never gives us a frame to open, so we are forced to close the flag without having a frame!
            pass # TODO: ?

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
        self.state = state
        self.objects = []
        self.object_debuts = {}
        self.class_frames_by_frame = {}
        self.class_frames_by_class = {}
        self.generator_frames = {}
        self.generator_functs = {}
        self.function_parents = {}

    def step(self):
        """
        <summary>

        :return:
        """
        if isinstance(self.state.program_state.curr_element, pyagram_element.PyagramFrame):
            curr_frame = self.state.program_state.curr_element
            for object in self.objects:
                if not pyagram_types.is_builtin_type(object):

                    object_type = type(object)
                    if object_type in pyagram_types.FUNCTION_TYPES:
                        self.record_parent(curr_frame, object)
                        referents = utils.get_defaults(object)
                    elif object_type in pyagram_types.BUILTIN_FUNCTION_TYPES:
                        referents = []
                    elif object_type in pyagram_types.ORDERED_COLLECTION_TYPES:
                        # TODO: Here where you use gc, you don't actually need it. For ORDERED_COLLECTION_TYPES you can just do something like `iter(object)`, or maybe just `object`. Similar for UNORDERED_COLLECTION_TYPES. For MAPPING_TYPES it's a bit more complex, but not by much -- you just have to get all the keys and values in the mapping.
                        referents = gc.get_referents(object)
                    elif object_type in pyagram_types.UNORDERED_COLLECTION_TYPES:
                        referents = gc.get_referents(object)
                    elif object_type in pyagram_types.MAPPING_TYPES:
                        referents = gc.get_referents(object)
                    elif object_type in pyagram_types.ITERATOR_TYPES:
                        iterable = pyagram_types.get_iterable(object)
                        referents = [] if iterable is None else [iterable]
                    elif object_type in pyagram_types.GENERATOR_TYPES:
                        referents = list(inspect.getgeneratorlocals(object).values())
                        if object.gi_yieldfrom is not None:
                            referents.append(object.gi_yieldfrom)
                    elif object_type is pyagram_wrapped_object.PyagramClassFrame:
                        referents = [
                            value
                            for key, value in object.bindings.items()
                            if key not in pyagram_wrapped_object.PyagramClassFrame.HIDDEN_BINDINGS
                        ]
                    elif hasattr(object, '__dict__'):
                        referents = object.__dict__.values()
                    else:
                        referents = []

                    for referent in referents:
                        self.track(referent)
            curr_frame.is_new_frame = False

    def snapshot(self):
        """
        <summary>

        :return:
        """
        return [
            {
                'id': object.id if isinstance(object, pyagram_wrapped_object.PyagramClassFrame) else id(object),
                'object': self.state.encoder.object_snapshot(object, self),
            }
            for object in self.objects
        ]

    def track(self, object):
        """
        <summary>

        :return:
        """
        is_object = not pyagram_types.is_primitive_type(object)
        is_unseen = not self.is_tracked(object)
        is_masked = isinstance(object, type) and object in self.class_frames_by_class
        if is_object and is_unseen and not is_masked:
            debut_index = len(self.state.snapshots)
            self.objects.append(object)
            self.object_debuts[id(object)] = debut_index
            if inspect.isgenerator(object):
                self.generator_functs[object] = utils.get_function(object.gi_frame)

    def is_tracked(self, object):
        """
        <summary>

        :param object:
        :return:
        """
        return id(object) in self.object_debuts

    def record_class_frame(self, frame_object, class_object):
        class_frame = self.class_frames_by_frame[frame_object]
        self.class_frames_by_class[class_object] = class_frame
        class_frame.id = id(class_object)
        class_frame.parents = class_object.__bases__
        class_frame.bindings = class_object.__dict__

    def record_generator_frame(self, pyagram_frame):
        generator = None
        for object in gc.get_referrers(pyagram_frame.frame):
            if inspect.isgenerator(object):
                assert generator is None, f'multiple generators refer to frame object {pyagram_frame.frame}'
                generator = object
        if generator in self.generator_frames:
            assert self.generator_frames[generator].frame is pyagram_frame.frame
        self.generator_frames[generator] = pyagram_frame
        self.track(generator)

    def record_parent(self, frame, function):
        """
        <summary>

        :param frame:
        :param function:
        :return:
        """
        if function not in self.function_parents:
            utils.assign_unique_code_object(function)
            if not frame.is_global_frame and frame.is_new_frame:
                parent = frame.opened_by
                while isinstance(parent, pyagram_element.PyagramFlag):
                    parent = parent.opened_by
            else:
                parent = frame
            self.function_parents[function] = parent

# TODO: This doesn't work ...
# l_half = [0, 1, 2]
# r_half = [3, 4, 5]
# lst = min(l_half, r_half, key=lambda lst: lst[0])
# TODO: ... because of the nested flags in the hidden flag. I think we should actually omit subflags of hidden flags, except in the case of generators which are handled specially.

# TODO: REALLY GOOD NEWS! It takes a long time to run a query -- but not inherently. It appears most of the time is actually coming from the call to render_components in app.py, so you can speed it up a LOT by rendering on-the-fly instead!

# TODO: In this code ...
# class A:
#     x = 1
#     class B:
#         x = 2
#     class C:
#         x = 3
#     x = 4
# You're skipping the 5th snapshot. There should be one step in which you bind B in A's frame, and a different step in which you start working on Class C.
# Snapshot on line 129?
# TODO: Also you're taking too many snapshots with iterators. Possibly generators too.

# TODO: Generators
# TODO: Basically we don't want a flag or frame for it. Instead we want to display the frame as an object frame, even though it isn't really.
# TODO: (1) If a flag is in hidden_flags, hide it -- but NOT its subflags! (2) Make the generator flag hidden.
# def fib():
#     prev, cur = 0, 1
#     while True:
#         yield prev
#         prev, cur = cur, prev + cur
# def g(x):
#     return x
# f = fib()
# a = next(f)
# b = next(f)
# c = next(fib())
# d = next(g(f))
# e = next(g(fib()))
# TODO: also ...
# def g(lst):
#     yield [a]
#     yield 2
#     yield from lst
#     yield from ls2
#     yield 9
# a = g([3, 4, 5])
# ls2 = [6, 7, 8]
# while True:
#     x = next(a)
# TODO: Right now it looks like it yields None right before StopIteration. Fix that.

# TODO: What if you did something like this, where you change the __dict__ but the key isn't a string anymore? How do you want to represent that? Also, depending, make sure to track() the right stuff! Or do we just not support this behavior?
# class A:
#     pass
# a = A()
# a.__dict__ = {a: 1}

# TODO: Make magic methods display nice. Both flags are wrong here ...
# class A:
#     def __init__(self): # TODO: If the frame.function is a class' .__init__, then modify the flag banner accordingly.
#         pass
#     def __lt__(self, other):
#         return True
# a = A()
# b = A()
# c = a < b

# TODO: Bound methods should not be visualized. Instead of a pointer to a particular bound function, you should see a pointer to the function on which it's based (ie its .__func__). This is unfortunate but necessary behavior, since it's impossible to tell, given just the code object, whether you're calling a function or the bound method based on that function. Similar behavior for wrappers, descriptors, etc.
# def f():
#     class A:
#         def f(self):
#             return 0
#     return A
# A = f()
# a = A()
# b = A()
# c = a.f()
# a.f = b.f
# xyz = a.f
# A.f = lambda x: 1
# d = a.f()
# e = A.f(a)
# TODO: Make sure methods and bound methods of classes and instances work fine.
# TODO: I think inspect.signature may not play well with Methods. Look at all the places you use it. You can't treat functions and methods the same.
# TODO: FYI, <method>.__self__ is a pointer to the instance to which the method is bound, or None. Might be useful for visually representing bound methods?
# Functions, unbound methods, and <slot wrapper>s should display the same way.
# Bound methods include a <bound method> type, and a <method-wrapper> type.

# TODO: Make built-in objects display nice.
# (*) Why do the slot wrappers and method descriptors not show up like other functions? Fix that.
# (*) Maybe if the repr is of the form <CLASS INSTANCE_NAME at 0xHEXADECIMAL> you can instead display it as you display other instances, i.e. a box with "CLASS instance" written inside? Things like None and NotImplemented should still be represented the same way though, as just the word None or NotImplemented according to their repr.
# (*) This displays horribly! Maybe if the object is an INSTANCE of the `type` class then (1) draw it like one of your PyagramClassFrames; (2) write a `...` somewhere; and (3) omit most of the contents by adding it all to `ignored`.
# a = object()
# b = IndexError('Oops.')
# x = object
# y = IndexError

# TODO: Try / except statements

# TODO: Comprehensions (list comp, dict comp, genexp, etc.)

# TODO: Why is `__name__` bound to `'builtins'`?
