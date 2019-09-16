import copy

import display
import enums
import pyagram_elements

class ProgramState:
    """
    <summary> # a mutable object representing the state of the program at the current timestep. as we go thru the program in trace.py, we will modify the ProgramState.

    :param global_frame:
    """

    def __init__(self, global_frame):
        self.global_frame = pyagram_elements.PyagramFrame(None, global_frame)
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
        is_flag = isinstance(self.curr_element, pyagram_elements.PyagramFlag)
        return is_flag and self.curr_element.frame is None

    @property
    def is_ongoing_frame(self):
        """
        <summary>

        :return:
        """
        is_frame = isinstance(self.curr_element, pyagram_elements.PyagramFrame)
        return is_frame and not self.curr_element.has_returned

    @property
    def is_complete_flag(self):
        """
        <summary>

        :return:
        """
        is_flag = isinstance(self.curr_element, pyagram_elements.PyagramFlag)
        return is_flag and self.curr_element.has_returned

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
                while isinstance(parent, pyagram_elements.PyagramFlag):
                    parent = parent.opened_by
            else:
                parent = frame
            self.function_parents[function] = parent
