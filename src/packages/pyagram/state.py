from . import enums
from . import pyagram_element
from . import utils

class State:
    """
    The instantaneous state of the pyagram at a particular step during the execution of the input
    code.

    The state consists of the following:
    * The state of the program.
    * The state of the memory.
    * The sequence of strings printed by the input code in the current step and all previous.

    :param global_frame:
    """

    def __init__(self, global_frame, encoder, stdout):
        self.num_pyagram_flags, self.num_pyagram_frames = 0, 0
        self.program_state = ProgramState(self, global_frame)
        self.memory_state = MemoryState(self)
        self.print_output = stdout
        self.hidden_flags = []
        self.encoder = encoder
        self.snapshots = []

    def step(self, frame, is_frame_open=None, is_frame_close=None, return_value=None):
        """
        <summary> # may also pass in frame=None, eg in PyagramFrame.close

        :param frame: As in trace.Tracer.step.
        :param is_frame_open: As in trace.Tracer.step.
        :param is_frame_close: As in trace.Tracer.step.
        :param return_value: As in trace.Tracer.step.
        :return: None.
        """
        self.program_state.step(frame, is_frame_open, is_frame_close, return_value)
        self.memory_state.step()

    def snapshot(self):
        """
        <summary> # Represents the state at a particular step in time.

        :return:
        """
        snapshot = {
            'program_state': self.program_state.snapshot(),
            'memory_state': self.memory_state.snapshot(),
            'print_output': self.print_output.getvalue().split('\n'),
        }
        self.snapshots.append(snapshot)

class ProgramState:
    """
    The instantaneous state of the program at a particular step during the execution of the input
    code. It includes all flags, frames, and bindings in the pyagram.

    :param state:
    :param global_frame:
    """

    def __init__(self, state, global_frame):
        self.frame_types = {}
        self.curr_line_no = None
        self.global_frame = pyagram_element.PyagramFrame(None, global_frame, state=state)
        self.curr_element = self.global_frame

    @property
    def is_ongoing_flag_sans_frame(self):
        """
        <summary>

        :return:
        """
        is_flag = isinstance(self.curr_element, pyagram_element.PyagramFlag)
        return is_flag and self.curr_element.frame is None

    @property
    def is_ongoing_frame(self):
        """
        <summary>

        :return:
        """
        is_frame = isinstance(self.curr_element, pyagram_element.PyagramFrame)
        return is_frame and not self.curr_element.has_returned

    @property
    def is_complete_flag(self):
        """
        <summary>

        :return:
        """
        is_flag = isinstance(self.curr_element, pyagram_element.PyagramFlag)
        return is_flag and self.curr_element.has_returned

    def step(self, frame, is_frame_open, is_frame_close, return_value):
        """
        <summary>

        :param frame: As in state.State.step.
        :param is_frame_open: As in state.State.step.
        :param is_frame_close: As in state.State.step.
        :param return_value: As in state.State.step.
        :return: None.
        """
        if frame is not None:
            if frame not in self.frame_types:
                # TODO: A frame's f_lineno changes over time. Either (A) verify that when you insert the frame into self.frame_types, the f_lineno is definitely correct (I'm not sure if this preprocess.py alone guarantees this), or (B) find a new way to identify whether a frame is a SRC_CALL, SRC_CALL_PRECURSOR, or SRC_CALL_SUCCESSOR frame.
                self.frame_types[frame] = enums.FrameTypes.identify_frame_type(frame)
            frame_type = self.frame_types[frame]
            self.curr_line_no = frame.f_lineno
            if is_frame_open:
                self.process_frame_open(frame, frame_type)
            if is_frame_close:
                self.process_frame_close(frame, frame_type, return_value)
        self.global_frame.step()

    def snapshot(self):
        """
        <summary>

        :return:
        """
        return {
            'global_frame': self.global_frame.snapshot(),
            'curr_line_no': self.curr_line_no, # TODO: This is either: (*) accurate, (*) utils.INNER_CALL_LINENO, (*) utils.OUTER_CALL_LINENO, or (*) greater than the total number of lines in the program. If you observe the lattermost case, then we are in fact executing a lambda function, and you can extract the appropriate line number using utils.unpair_naturals. See encode.py for an example.
        }

    def process_frame_open(self, frame, frame_type):
        """
        <summary>

        :param frame:
        :param frame_type:
        :return:
        """
        if frame_type is enums.FrameTypes.SRC_CALL:

            is_implicit = self.is_ongoing_frame # An "implicit call" is when the user didn't invoke the function directly. eg the user instantiates a class, and __init__ gets called implicitly.
            if is_implicit:
                self.open_pyagram_flag(banner=None) # TODO: what is the appropriate banner for an implicit call?
            self.open_pyagram_frame(frame, is_implicit)

        elif frame_type is enums.FrameTypes.SRC_CALL_PRECURSOR:
            pass
        elif frame_type is enums.FrameTypes.SRC_CALL_SUCCESSOR:
            self.close_pyagram_flag()
        else:
            raise enums.FrameTypes.illegal_frame_type(frame_type)

    def process_frame_close(self, frame, frame_type, return_value):
        """
        <summary>

        :param frame:
        :param frame_type:
        :param return_value:
        :return:
        """
        if frame_type is enums.FrameTypes.SRC_CALL:
            self.close_pyagram_frame(return_value)
        elif frame_type is enums.FrameTypes.SRC_CALL_PRECURSOR:
            self.open_pyagram_flag(return_value)
        elif frame_type is enums.FrameTypes.SRC_CALL_SUCCESSOR:
            pass
        else:
            raise enums.FrameTypes.illegal_frame_type(frame_type)

    def open_pyagram_flag(self, banner):
        """
        <summary>

        :param banner:
        :return:
        """
        assert self.is_ongoing_flag_sans_frame or self.is_ongoing_frame
        self.curr_element = self.curr_element.add_flag(banner)

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
            # If we call a built-in function, we open a flag but bdb never gives us a frame to open, so we are forced to close the flag without having a frame!
            pass
            # TODO: Add a 'fake' frame that displays the return value.
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

class MemoryState:
    """
    The instantaneous state of the memory at a particular step during the execution of the input
    code. It includes all referent objects in the pyagram.
    """

    def __init__(self, state):
        self.state = state
        self.objects = [] # TODO: Make sure that every object gets displayed in the same place on the web-page, across different steps of the visualization. One approach: render the last step first (since it will have all the objects visualized); then make sure every object gets drawn in the same place in every previous step.
        self.object_debuts = {}
        self.function_parents = {}

    def step(self):
        """
        <summary>

        :return:
        """
        pass

    def snapshot(self):
        """
        <summary>

        :return:
        """
        return [
            {
                'id': id(object),
                'object': self.state.encoder.object_snapshot(object, self),
            }
            for object in self.objects
        ]

    def track(self, object, debut_index): # TODO: The argument for debut_index is always `len(self.state.snapshots)`. Just get rid of it as a parameter, and instead add the line `debut_index = len(self.state.snapshots)` below.
        """
        <summary>

        :return:
        """
        if not self.is_tracked(object):
            self.objects.append(object)
            self.object_debuts[id(object)] = debut_index

    def is_tracked(self, object):
        """
        <summary>

        :param object:
        :return:
        """
        return id(object) in self.object_debuts

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
