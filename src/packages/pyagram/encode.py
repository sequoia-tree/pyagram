import inspect

from . import enum
from . import pyagram_element
from . import pyagram_types
from . import pyagram_wrapped_object
from . import utils

class Encoder:
    """
    """

    def __init__(self, state, preprocessor_summary):
        self.state = state
        num_lines, lambdas_per_line = preprocessor_summary
        self.num_lines = num_lines
        self.lambdas_per_line = lambdas_per_line

    def reference_snapshot(self, object):
        """
        """
        if object is enum.ObjectTypes.UNKNOWN:
            return None
        object_type = enum.ObjectTypes.identify_object_type(object)
        if object_type is enum.ObjectTypes.PRIMITIVE:
            return self.encode_primitive(object)
        else:
            return id(object)

    def object_snapshot(self, object):
        """
        """
        object_type = enum.ObjectTypes.identify_object_type(object)
        if object_type is enum.ObjectTypes.PRIMITIVE:
            encoding = 'primitive'
            data = self.encode_primitive(object)
        elif object_type is enum.ObjectTypes.FUNCTION:
            encoding = 'function'
            data = self.encode_function(object)
        elif object_type is enum.ObjectTypes.BUILTIN:
            encoding = 'builtin'
            data = self.encode_builtin(object)
        elif object_type is enum.ObjectTypes.ORDERED_COLLECTION:
            encoding = 'ordered_collection'
            data = self.encode_collection(object)
        elif object_type is enum.ObjectTypes.UNORDERED_COLLECTION:
            encoding = 'unordered_collection'
            data = self.encode_collection(object)
        elif object_type is enum.ObjectTypes.MAPPING:
            encoding = 'mapping'
            data = self.encode_mapping(object)
        elif object_type is enum.ObjectTypes.ITERATOR:
            encoding = 'iterator'
            data = self.encode_iterator(object)
        elif object_type is enum.ObjectTypes.GENERATOR:
            encoding = 'generator'
            data = self.encode_generator(object)
        elif object_type is enum.ObjectTypes.OBJ_CLASS:
            encoding = 'obj_class'
            data = self.encode_obj_class(object)
        elif object_type is enum.ObjectTypes.OBJ_INST:
            encoding = 'obj_inst'
            data = self.encode_obj_inst(object)
        elif object_type is enum.ObjectTypes.OTHER:
            encoding = 'other'
            data = self.encode_other(object)
        else:
            raise enum.ObjectTypes.illegal_enum(object_type)
        return {
            'encoding': encoding,
            'data': data,
        }

    def encode_primitive(self, object):
        """
        """
        return repr(object) if type(object) is str else str(object)

    def encode_function(self, object):
        """
        """
        is_lambda = object.__name__ == '<lambda>'
        if is_lambda:
            lineno, _, lambda_number = utils.decode_lineno(
                object.__code__.co_firstlineno,
                max_lineno=self.num_lines,
            )
        parameters, slash_arg_index, has_star_arg = [], None, False
        for i, parameter in enumerate(inspect.signature(object).parameters.values()):
            if parameter.kind is inspect.Parameter.POSITIONAL_ONLY:
                slash_arg_index = i + 1
            elif parameter.kind is inspect.Parameter.VAR_POSITIONAL:
                has_star_arg = True
            elif parameter.kind is inspect.Parameter.KEYWORD_ONLY and not has_star_arg:
                parameters.append({
                    'name': '*',
                    'default': None,
                })
                has_star_arg = True
            parameters.append({
                'name':
                    str(parameter)
                    if parameter.default is inspect.Parameter.empty
                    else str(parameter).split('=', 1)[0],
                'default':
                    None
                    if parameter.default is inspect.Parameter.empty
                    else self.reference_snapshot(parameter.default),
            })
        if slash_arg_index is not None:
            slash_arg = {
                'name': '/',
                'default': None,
            }
            parameters.insert(slash_arg_index, slash_arg)
        return {
                'is_gen_func': inspect.isgeneratorfunction(object),
                'name': object.__name__,
                'lambda_id':
                    {
                        'lineno': lineno,
                        'number': lambda_number,
                        'single': self.lambdas_per_line[lineno] == 1,
                    }
                    if is_lambda
                    else None,
                'parameters': parameters,
                'parent': repr(self.state.memory_state.function_parents[object]),
            }

    def encode_builtin(self, object):
        """
        """
        return object.__name__

    def encode_collection(self, object):
        """
        """
        return {
            'type': type(object).__name__,
            'elements': [
                self.reference_snapshot(item)
                for item in object
            ],
        }

    def encode_mapping(self, object):
        """
        """
        return {
            'type': type(object).__name__,
            'items': [
                {
                    'key': self.reference_snapshot(key),
                    'value': self.reference_snapshot(value),
                }
                for key, value in object.items()
            ],
        }

    def encode_iterator(self, object):
        """
        """
        iterable = pyagram_types.get_iterable(object)
        return None if iterable is None else {
            'object': self.reference_snapshot(iterable),
            'index': len(iterable) - object.__length_hint__(),
            'annotation': pyagram_types.ITERATOR_TYPE_MAP[type(object)][1],
        }

    def encode_generator(self, object):
        """
        """
        # TODO: Refactor this func
        memory_state = self.state.memory_state
        snapshot = {
            'name': object.__name__,
            'parents': [repr(memory_state.function_parents[memory_state.generator_functs[object]])],
            'bindings': {
                key: self.reference_snapshot(value)
                for key, value in inspect.getgeneratorlocals(object).items()
            },
            'flags': [],
        }
        if object in memory_state.generator_frames:
            frame = memory_state.generator_frames[object]
            snapshot.update({
                'is_curr_element': frame is self.state.program_state.curr_element,
                'return_value':
                    self.reference_snapshot(frame.return_value)
                    if frame.has_returned
                    else None,
                'from': None if object.gi_yieldfrom is None else self.reference_snapshot(object.gi_yieldfrom),
            })
        else:
            snapshot.update({
                'is_curr_element': False,
                'return_value': None,
                'from': None,
            })
        return snapshot

    def encode_obj_class(self, object):
        """
        """
        # TODO: Refactor this func
        return {
            'is_curr_element': False,
            'name': object.frame.f_code.co_name,
            'parents': None, # Placeholder.
            'bindings': {
                key: self.reference_snapshot(value)
                for key, value in object.bindings.items()
                if key not in pyagram_wrapped_object.PyagramClassFrame.HIDDEN_BINDINGS
            },
            'return_value': None,
            'flags': [],
            'self': object, # For postprocessing.
        }
        # TODO: Consider this.
        # (*) Introduce a new attribute, curr_class, which is initially bound to None. When you open a class frame: (1) set the class frame's opened_by equal to the curr_class; (2) set the curr_class equal to the newly-opened class frame. When you close a class frame, set the curr_class equal to the class frame's opened_by.
        # (*) If the curr_class is not None, and the curr_elem is the PyagramFrame that you were in when you instantiated the curr_class, then the green background should go behind the class frame -- not the program frame.
        # (*) Make sure this works for nested classdefs interleaved with function calls.

    def encode_obj_inst(self, object):
        """
        """
        # TODO: Refactor this func
        return {
            'is_curr_element': False,
            'name': type(object).__name__,
            'parents': [],
            'bindings': {
                key: self.reference_snapshot(value)
                for key, value in object.__dict__.items()
            },
            'return_value': None,
            'flags': [],
        }
        # TODO: Might some objects have a lot of items in their __dict__? Some ideas ...
        # (*) Make it an option [default ON] to render the contents in object frames.
        # (*) Limit the size of each object frame, but make the contents scrollable on the site.
        # (*) Include a button next to each object frame, which you can click to toggle whether to render the contents of that particular object frame.

    def encode_other(self, object):
        """
        """
        return repr(object)
