import wrap

class TraceTypes:
    """
    <summary> # basically this is like an Enum class
    """

    USER_CALL = object()
    USER_LINE = object()
    USER_RETURN = object()
    USER_EXCEPTION = object()

    @staticmethod
    def illegal_trace_type(trace_type):
        """
        <summary>

        :param frame:
        :return:
        """
        return ValueError(f'object {trace_type} is not a TraceTypes enumeral')

class FrameTypes:
    """
    <summary> # basically this is like an Enum class
    """

    SRC_CALL_PRECURSOR = object()
    SRC_CALL = object()
    SRC_CALL_SUCCESSOR = object()

    @staticmethod
    def illegal_frame_type(frame_type):
        """
        <summary>

        :param frame:
        :return:
        """
        return ValueError(f'object {frame_type} is not a FrameTypes enumeral')

    @staticmethod
    def identify_frame_type(frame):
        """
        <summary>

        :param frame:
        :return:
        """

        # If the frame is a SRC_CALL_PRECURSOR, it's the frame for one of the "fake" inner_lambda functions we created in wrap.py. If it's a SRC_CALL_SUCCESSOR, it's the frame for one of the "fake" outer_lambda functions we created in wrap.py.

        lineno = frame.f_lineno
        if lineno == wrap.INNER_CALL_LINENO:
            return FrameTypes.SRC_CALL_PRECURSOR
        if lineno == wrap.OUTER_CALL_LINENO:
            return FrameTypes.SRC_CALL_SUCCESSOR
        assert 0 < lineno
        return FrameTypes.SRC_CALL
