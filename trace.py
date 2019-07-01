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

    def user_call(self, frame, argument_list):
        """
        <summary>

        :param frame: the frame that gets opened
        :param argument_list: the arguments to the function call
        :return:
        """
        self.make_snapshot(frame, True)

    def user_line(self, frame):
        """
        <summary>

        :param frame:
        :return:
        """
        self.make_snapshot(frame)

    def user_return(self, frame, return_value):
        """
        <summary>

        :param frame:
        :param return_value:
        :return:
        """
        self.state.process_frame_close(frame, return_value)
        self.make_snapshot(frame)

    def user_exception(self, frame, exception_info):
        """
        <summary>

        :param frame:
        :param exception_info:
        :return:
        """
        # TODO: Figure out how you want to address exceptions.
        self.make_snapshot(frame)

    def make_snapshot(self, frame, is_new_frame=False):
        """
        <summary>

        :param frame:
        :param is_new_frame:
        :return:
        """
        if self.state is None:
            self.state = models.ProgramState(frame)
        if is_new_frame:
            self.state.process_frame_open(frame)
        snapshot = self.state.snapshot()
        self.snapshots.append(snapshot)
        snapshot.display() # For debugging.
