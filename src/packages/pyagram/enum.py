from . import configs

class Enum:
    """
    """

    @staticmethod
    def illegal_enum(illegal_enum):
        return ValueError(f'object {illegal_enum} is not an enumeral')

class TraceTypes(Enum):
    """
    """

    USER_CALL = object()
    USER_LINE = object()
    USER_RETURN = object()
    USER_EXCEPTION = object()

class FrameTypes(Enum):
    """
    """

    SRC_CALL_PRECURSOR = object()
    SRC_CALL = object()
    SRC_CALL_SUCCESSOR = object()
    CLASS_DEFINITION = object()

    @staticmethod
    def identify_frame_type(frame):
        """
        <summary>

        :param frame:
        :return:
        """

        # If the frame is a SRC_CALL_PRECURSOR, it's the frame for one of the "fake" inner_lambda functions we created in wrap.py. If it's a SRC_CALL_SUCCESSOR, it's the frame for one of the "fake" outer_lambda functions we created in wrap.py.

        lineno = frame.f_lineno
        if lineno == configs.INNER_CALL_LINENO:
            return FrameTypes.SRC_CALL_PRECURSOR
        if lineno == configs.OUTER_CALL_LINENO:
            return FrameTypes.SRC_CALL_SUCCESSOR
        if lineno == configs.CLASS_DEFN_LINENO:
            return FrameTypes.CLASS_DEFINITION
        assert 0 < lineno
        return FrameTypes.SRC_CALL
