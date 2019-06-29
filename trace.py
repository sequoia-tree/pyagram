import bdb
import inspect

import models # TODO: Or some file that does the reverse-engineering, which imports models.

class Tracer(bdb.Bdb):
    """
    <summary>
    """

    def __init__(self, pyagram):
        """
        <summary>
        """
        super().__init__()
        self.pyagram = pyagram
        self.frames = []
        self.return_values = {}

    def user_call(self, frame, argument_list):
        """
        <summary>

        :param frame: the frame that gets opened
        :param argument_list: the arguments to the function call
        :return:
        """
        self.update_frames(frame, True)

    def user_line(self, frame):
        """
        <summary>

        :param frame:
        :return:
        """
        self.update_frames(frame)

    def user_return(self, frame, return_value):
        """
        <summary>

        :param frame:
        :param return_value:
        :return:
        """
        self.return_values[frame] = return_value
        self.update_frames(frame)

    def user_exception(self, frame, exception_info):
        """
        <summary>

        :param frame:
        :param exception_info:
        :return:
        """
        self.update_frames(frame)

    def update_frames(self, frame, is_new_frame=False):
        """
        <summary> # Update the bindings in `frame`, according to the new state of the program.

        :param frame:
        :param is_new_frame:
        :return:
        """
        is_global_frame = len(self.frames) == 0
        if is_global_frame or is_new_frame:
            self.frames.append(frame)
        # self.print_all_frames()

        # TODO: ^ Don't delete that comment, it's good for debugging.

        # TODO: Update self.pyagram.

        # TODO: frame.f_lineno is the line number last evaluated. We want this info!
        # TODO: Maybe useful ... frame.f_locals and frame.f_globals


    def print_all_frames(self):
        """
        <summary> # for debugging

        :return:
        """
        for num, frame in enumerate(self.frames):
            # TODO: If you keep this function around, give the frame a __repr__.
            print(f'Frame {num}: {frame.f_locals}')
            if self.return_values.get(frame, False):
                print(f'\tReturn: {repr(self.return_values[frame])}')
        print('')
