import bdb

from . import enums
from . import exception
from . import state
from . import utils

class Tracer(bdb.Bdb):
    """
    <summary>
    """

    def __init__(self, encoder, stdout):
        super().__init__()
        self.encoder = encoder
        self.stdout = stdout
        self.state = None

    def user_call(self, frame, args):
        """
        <summary>

        :param frame: the frame that gets opened
        :param args: the arguments to the function call (pretty sure this is deprecated tho)
        :return:
        """
        self.step(frame, is_frame_open=True)
        self.snapshot(enums.TraceTypes.USER_CALL)

    def user_line(self, frame):
        """
        <summary>

        :param frame:
        :return:
        """
        self.step(frame)
        self.snapshot(enums.TraceTypes.USER_LINE)

    def user_return(self, frame, return_value):
        """
        <summary>

        :param frame:
        :param return_value:
        :return:
        """
        self.step(frame, is_frame_close=True, return_value=return_value)
        self.snapshot(enums.TraceTypes.USER_RETURN)

    def user_exception(self, frame, exception_info):
        """
        <summary>

        :param frame:
        :param exception_info:
        :return:
        """
        # TODO: Figure out how you want to address exceptions.
        # TODO: If there is an error, then don't do any of the flag banner nonsense.
        # TODO: Your code relies on a program that works; therefore if the code doesn't work, your code will throw some error that is different from the one thrown by the input code. If there's an error, perhaps run the student's code plain-out and scrape its error message?
        self.snapshot(enums.TraceTypes.USER_EXCEPTION)
        raise exception.UserException(*exception_info)

    def step(self, frame, *, is_frame_open=False, is_frame_close=False, return_value=None):
        """
        <summary>

        :param frame:
        :param is_frame_open:
        :param is_frame_close:
        :param return_value:
        :return:
        """
        if self.state is None:
            self.state = state.State(frame, self.encoder, self.stdout)
        self.state.step(frame, is_frame_open, is_frame_close, return_value)

    def snapshot(self, trace_type):
        """
        <summary>

        :return:
        """
        if self.state.program_state.curr_element is None:
            take_snapshot = False
        elif trace_type is enums.TraceTypes.USER_CALL:
            take_snapshot = False
        elif trace_type is enums.TraceTypes.USER_LINE:
            take_snapshot = self.state.program_state.prev_line_no != utils.INNER_CALL_LINENO \
                        and self.state.program_state.prev_line_no != utils.OUTER_CALL_LINENO \
                        and not self.state.program_state.is_complete_flag
        elif trace_type is enums.TraceTypes.USER_RETURN:
            take_snapshot = not self.state.program_state.is_complete_flag
        elif trace_type is enums.TraceTypes.USER_EXCEPTION:
            take_snapshot = False
        else:
            raise enums.TraceTypes.illegal_trace_type(trace_type)
        # TODO: This still isn't quite perfect. You take duplicate snapshots in some cases, which get pruned out during postprocessing, but it'd be much more efficient if you could get this right.
        if take_snapshot:
            self.state.snapshot()
