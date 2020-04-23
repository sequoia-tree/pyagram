from . import configs

class Enum:
    """
    """

    @staticmethod
    def illegal_enum(illegal_enum):
        return ValueError(f'not an enumeral: {illegal_enum}')

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
    def identify_frame_type(step_code):
        """
        """
        # if step_code == configs.UNMODIFIED_LINENO:
        #     return FrameTypes.SRC_CALL
        # elif step_code == configs.INNER_CALL_LINENO:
        #     return FrameTypes.SRC_CALL_PRECURSOR
        # elif step_code == configs.OUTER_CALL_LINENO:
        #     return FrameTypes.SRC_CALL_SUCCESSOR
        # elif step_code == configs.CLASS_DEFN_LINENO:
        #     return FrameTypes.CLASS_DEFINITION
        # else:
        #     raise FrameTypes.illegal_enum(step_code)

        frame = step_code
        lineno = frame.f_lineno
        if lineno == configs.INNER_CALL_LINENO:
            return FrameTypes.SRC_CALL_PRECURSOR
        if lineno == configs.OUTER_CALL_LINENO:
            return FrameTypes.SRC_CALL_SUCCESSOR
        if lineno == configs.CLASS_DEFN_LINENO:
            return FrameTypes.CLASS_DEFINITION
        assert 0 < lineno
        return FrameTypes.SRC_CALL
