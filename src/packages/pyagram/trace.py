import bdb

from . import enum

class Tracer(bdb.Bdb):
    """
    """

    def __init__(self, state):
        super().__init__()
        self.state = state

    def user_call(self, frame, args):
        """
        """
        self.state.step(frame, trace_type=enum.TraceTypes.USER_CALL)

    def user_line(self, frame):
        """
        """
        self.state.step(frame, trace_type=enum.TraceTypes.USER_LINE)

    def user_return(self, frame, return_value):
        """
        """
        print('RET')
        self.state.step(frame, return_value, trace_type=enum.TraceTypes.USER_RETURN)

    def user_exception(self, frame, exception_info):
        """
        """
        print('EXCEPTION in', self.state.program_state.curr_element)
        self.state.step(frame, exception_info, trace_type=enum.TraceTypes.USER_EXCEPTION)
