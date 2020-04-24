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
        # TODO: Refactor this func
        if object is enum.ObjectTypes.UNKNOWN:
            return {'cls': 'unknown', 'text': '<?>'} # TODO: Messy
        elif pyagram_types.is_primitive_type(object):
            return repr(object) if isinstance(object, str) else str(object)
        else:
            return id(object)

    def object_snapshot(self, object):
        """
        """
        # TODO: Refactor this func
        state = self.state
        memory_state = state.memory_state
        object_type = type(object)
        if object_type in pyagram_types.FUNCTION_TYPES:
            is_lambda = object.__name__ == '<lambda>'
            if is_lambda:
                assert object.__code__.co_firstlineno > self.num_lines
                lineno, _, lambda_number = utils.decode_lineno(object.__code__.co_firstlineno, max_lineno=self.num_lines)
                number = lambda_number
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
                    'name': str(parameter) if parameter.default is inspect.Parameter.empty else str(parameter).split('=', 1)[0],
                    'default': None if parameter.default is inspect.Parameter.empty else self.reference_snapshot(parameter.default),
                })
            if slash_arg_index is not None:
                parameters.insert(slash_arg_index, {
                    'name': '/',
                    'default': None,
                })
            encoding = 'function'
            snapshot = {
                'is_gen_func': inspect.isgeneratorfunction(object),
                'name': object.__name__,
                'lambda_id':
                    {
                        'lineno': lineno,
                        'number': number,
                        'single': self.lambdas_per_line[lineno] <= 1,
                    }
                    if is_lambda
                    else None,
                'parameters': parameters,
                'parent': repr(memory_state.function_parents[object]),
            }
        elif object_type in pyagram_types.BUILTIN_FUNCTION_TYPES:
            encoding = 'builtin_function'
            snapshot = {
                'name': object.__name__,
            }
        elif object_type in pyagram_types.ORDERED_COLLECTION_TYPES:
            encoding = 'ordered_collection'
            snapshot = {
                'type': object_type.__name__,
                'elements': [
                    self.reference_snapshot(item)
                    for item in object
                ],
            }
        elif object_type in pyagram_types.UNORDERED_COLLECTION_TYPES:
            encoding = 'unordered_collection'
            snapshot = {
                'type': object_type.__name__,
                'elements': [
                    self.reference_snapshot(item)
                    for item in object
                ],
            }
        elif object_type in pyagram_types.MAPPING_TYPES:
            encoding = 'mapping'
            snapshot =  {
                'type': object_type.__name__,
                'items': [
                    [self.reference_snapshot(key), self.reference_snapshot(value)]
                    for key, value in object.items()
                ],
            }
        elif object_type in pyagram_types.ITERATOR_TYPES:
            encoding = 'iterator'
            iterable = pyagram_types.get_iterable(object)
            snapshot = {
                'object': None,
            } if iterable is None else {
                'object': self.reference_snapshot(iterable),
                'index': len(iterable) - object.__length_hint__(),
                'annotation': pyagram_types.ITERATOR_TYPE_MAP[type(object)][1],
            }
        elif object_type in pyagram_types.GENERATOR_TYPES:
            encoding = 'generator'
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
                    'is_curr_element': frame is state.program_state.curr_element,
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
        elif object_type is pyagram_wrapped_object.PyagramClassFrame:
            encoding = 'class_frame'
            snapshot = {
                'is_curr_element': False,
                'name': object.frame.f_code.co_name,
                'parents': object,
                'bindings': {
                    key: self.reference_snapshot(value)
                    for key, value in object.bindings.items()
                    if key not in pyagram_wrapped_object.PyagramClassFrame.HIDDEN_BINDINGS
                },
                'return_value': None,
                'flags': [],
            }
        elif hasattr(object, '__dict__'):
            encoding = 'object_dict'
            snapshot = {
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
        else:
            encoding = 'object_repr'
            snapshot = {
                'repr': repr(object),
            }
        return {
            'encoding': encoding, # So the decoder knows the structure of `snapshot`.
            'object': snapshot,
        }
