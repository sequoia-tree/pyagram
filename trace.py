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
        self.state.get_frame(frame).terminate(return_value)
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
            # Make a frame, or maybe make a flag, or maybe terminate a flag.
            # Used to be self.frames.append(frame)
            # TODO: frame.f_lineno is the line number last evaluated. We want this info!
            # TODO: Maybe useful ... frame.f_locals and frame.f_globals
            pass
        snapshot = models.ProgramStateSnapshot(self.state)
        self.snapshots.append(snapshot)
        # print(snapshot)
