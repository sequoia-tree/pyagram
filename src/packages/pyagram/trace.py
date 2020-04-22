import bdb

from . import enum
from . import state

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
        """
        self.step(frame, trace_type=enum.TraceTypes.USER_CALL)

    def user_line(self, frame):
        """
        """
        self.step(frame, trace_type=enum.TraceTypes.USER_LINE)

    def user_return(self, frame, return_value):
        """
        """
        self.step(frame, return_value, trace_type=enum.TraceTypes.USER_RETURN)

    def user_exception(self, frame, exception_info):
        """
        """
        # TODO: Figure out how you want to address exceptions.
        # TODO: If there is an error, then don't do any of the flag banner nonsense.
        # TODO: Your code relies on a program that works; therefore if the code doesn't work, your code will throw some error that is different from the one thrown by the input code. If there's an error, perhaps run the student's code plain-out and scrape its error message?
        #self.snapshot(enum.TraceTypes.USER_EXCEPTION)
        # TODO: We only want to raise a UserException if the user doesn't catch their exception! For something like this ...
        # l = [1, 2, 3]
        # try:
        #     a = l[3]
        # except IndexError:
        #     print('hi')
        # TODO: ... the desired behavior is what it would do without the following line.
        #raise exception.UserException(*exception_info)
        pass # TODO

    def step(self, frame, *step_info, trace_type):
        """
        """
        if self.state is None:
            self.state = state.State(frame, self.encoder, self.stdout) # TODO: init state in pyagram.py
        self.state.step(frame, *step_info, trace_type=trace_type)
