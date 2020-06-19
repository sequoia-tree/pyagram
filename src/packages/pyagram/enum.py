import inspect

from . import constants
from . import exception
from . import pyagram_wrapped_object

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

    SRC_CALL = object()
    CALL_BANNER = object()
    COMP_BANNER = object()
    FN_WRAPPER = object()
    RG_WRAPPER = object()
    PG_WRAPPER = object()
    CLASS_DEFN = object()
    CNTNR_COMP = object()

    @staticmethod
    def identify_frame_type(step_code):
        """
        """
        if step_code == constants.UNMODIFIED_LINENO:
            return FrameTypes.SRC_CALL
        elif step_code == constants.INNER_CALL_LINENO:
            return FrameTypes.CALL_BANNER
        elif step_code == constants.INNER_COMP_LINENO:
            return FrameTypes.COMP_BANNER
        elif step_code == constants.FN_WRAPPER_LINENO:
            return FrameTypes.FN_WRAPPER
        elif step_code == constants.RG_WRAPPER_LINENO:
            return FrameTypes.RG_WRAPPER
        elif step_code == constants.PG_WRAPPER_LINENO:
            return FrameTypes.PG_WRAPPER
        elif step_code == constants.CLASS_DEFN_LINENO:
            return FrameTypes.CLASS_DEFN
        elif step_code == constants.CNTNR_COMP_LINENO:
            return FrameTypes.CNTNR_COMP
        else:
            raise FrameTypes.illegal_enum(step_code)

class PyagramFlagTypes(Enum):
    """
    """

    CALL = object()
    COMP = object()

class PyagramFrameTypes(Enum):
    """
    """

    GLOBAL = object()
    BUILTIN = object()
    FUNCTION = object()
    GENERATOR = object()
    CNTNR_COMP = object()

class UnpackingTypes(Enum):
    """
    """

    NORMAL = object()
    SINGLY_UNPACKED = object()
    DOUBLY_UNPACKED = object()

    @staticmethod
    def identify_unpacking_type(unpacking_code):
        """
        """
        if unpacking_code == constants.NORMAL_ARG:
            return UnpackingTypes.NORMAL
        elif unpacking_code == constants.SINGLY_UNPACKED_ARG:
            return UnpackingTypes.SINGLY_UNPACKED
        elif unpacking_code == constants.DOUBLY_UNPACKED_ARG:
            return UnpackingTypes.DOUBLY_UNPACKED
        else:
            raise UnpackingTypes.illegal_enum(unpacking_code)

class ReferenceTypes(Enum):
    """
    """

    OMITTED = object()
    UNKNOWN = object()
    DEFAULT = object()

    @staticmethod
    def identify_reference_type(object):
        if object is ReferenceTypes.OMITTED:
            return ReferenceTypes.OMITTED
        elif object is ReferenceTypes.UNKNOWN:
            return ReferenceTypes.UNKNOWN
        else:
            return ReferenceTypes.DEFAULT

class ObjectTypes(Enum):
    """
    """

    PRIMITIVE = object()
    FUNCTION = object()
    METHOD = object()
    BUILTIN = object()
    ORDERED_COLLECTION = object()
    UNORDERED_COLLECTION = object()
    MAPPING = object()
    ITERATOR = object()
    GENERATOR = object()
    USER_CLASS = object()
    BLTN_CLASS = object()
    INSTANCE = object()
    RANGE = object()
    SLICE = object()
    OTHER = object()

    @staticmethod
    def identify_raw_object_type(object):
        """
        """
        object_type = type(object)
        if object_type in constants.PRIMITIVE_TYPES:
            return ObjectTypes.PRIMITIVE
        elif object_type in constants.FUNCTION_TYPES:
            return ObjectTypes.FUNCTION
        elif object_type in constants.METHOD_TYPES:
            return ObjectTypes.METHOD
        elif object_type in constants.BUILTIN_TYPES:
            return ObjectTypes.BUILTIN
        elif object_type in constants.ORDERED_COLLECTION_TYPES:
            return ObjectTypes.ORDERED_COLLECTION
        elif object_type in constants.UNORDERED_COLLECTION_TYPES:
            return ObjectTypes.UNORDERED_COLLECTION
        elif object_type in constants.MAPPING_TYPES:
            return ObjectTypes.MAPPING
        elif object_type in constants.ITERATOR_TYPES:
            return ObjectTypes.ITERATOR
        elif object_type in constants.GENERATOR_TYPES:
            return ObjectTypes.GENERATOR
        else:
            return ObjectTypes.OTHER

    @staticmethod
    def identify_tracked_object_type(object):
        """
        """
        raw_object_type = ObjectTypes.identify_raw_object_type(object)
        if raw_object_type is ObjectTypes.OTHER:
            object_type = type(object)
            if object_type is pyagram_wrapped_object.PyagramGeneratorFrame:
                return ObjectTypes.GENERATOR
            elif object_type is pyagram_wrapped_object.PyagramClassFrame:
                return ObjectTypes.USER_CLASS
            elif object_type is range:
                return ObjectTypes.RANGE
            elif object_type is slice:
                return ObjectTypes.SLICE
            elif object_type is type:
                return ObjectTypes.BLTN_CLASS
            elif hasattr(object, '__dict__'):
                return ObjectTypes.INSTANCE
            else:
                return ObjectTypes.OTHER
        else:
            assert raw_object_type not in {
                ObjectTypes.PRIMITIVE,
                ObjectTypes.GENERATOR,
                ObjectTypes.USER_CLASS,
                ObjectTypes.BLTN_CLASS,
                ObjectTypes.INSTANCE,
            }
            return raw_object_type

class ErrorTypes(Enum):
    """
    """

    PYAGRAM = object()
    SYNTAX = object()

    @staticmethod
    def identify_error_type(error):
        error_type = type(error)
        if error_type is exception.PyagramError:
            return ErrorTypes.PYAGRAM
        elif issubclass(error_type, SyntaxError):
            return ErrorTypes.SYNTAX
        else:
            raise ErrorTypes.illegal_enum(error_type)
