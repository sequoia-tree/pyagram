import bdb

import models

class Tracer(bdb.Bdb):
    """
    <summary>
    """

    def __init__(self):
        super().__init__()
        self.state = None
        self.snapshots = []

    def user_call(self, frame, args):
        """
        <summary>

        :param frame: the frame that gets opened
        :param args: the arguments to the function call (pretty sure this is deprecated tho)
        :return:
        """
        self.step(frame, is_frame_open=True)
        self.snapshot()

    def user_line(self, frame):
        """
        <summary>

        :param frame:
        :return:
        """
        self.step(frame)
        self.snapshot()

    def user_return(self, frame, return_value):
        """
        <summary>

        :param frame:
        :param return_value:
        :return:
        """
        self.step(frame, is_frame_close=True, return_value=return_value)
        self.snapshot()

    def user_exception(self, frame, exception_info):
        """
        <summary>

        :param frame:
        :param exception_info:
        :return:
        """
        # TODO: Figure out how you want to address exceptions.
        self.step(frame)
        self.snapshot()

    def step(self, frame, is_frame_open=False, is_frame_close=False, return_value=None):
        """
        <summary>

        :param frame:
        :param is_frame_open:
        :param is_frame_close:
        :param return_value:
        :return:
        """
        if self.state is None:
            self.state = models.ProgramState(frame)
        self.state.step(frame, is_frame_open, is_frame_close, return_value)

    def snapshot(self):
        """
        <summary>

        :return:
        """
        snapshot = self.state.snapshot()
        self.snapshots.append(snapshot)
