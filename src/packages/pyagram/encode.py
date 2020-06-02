import inspect

from . import constants
from . import enum
from . import pyagram_element
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

    def object_id(self, object):
        """
        """

        # Get the ID that we use to track an object.

        raw_id = id(object)
        return self.state.memory_state.wrapped_obj_ids.get(raw_id, raw_id)

    def encode_pyagram_flag(self, pyagram_flag):
        """
        """
        is_hidden = pyagram_flag.is_hidden()
        if pyagram_flag.is_call_flag:
            flag_type = 'call'
        elif pyagram_flag.is_comp_flag:
            flag_type = 'comp'
        else:
            raise enum.PyagramFlagTypes.illegal_enum(pyagram_flag.flag_type)
        return {
            'type': flag_type,
            'is_curr_element': pyagram_flag is self.state.program_state.curr_element,
            'banner': [
                self.encode_banner_element(pyagram_flag, banner_element)
                for banner_element in pyagram_flag.banner_elements
            ],
            'frame':
                None
                if pyagram_flag.frame is None or is_hidden
                else self.encode_pyagram_frame(pyagram_flag.frame),
            'flags':
                []
                if pyagram_flag.hide_flags
                else [
                    self.encode_pyagram_flag(flag)
                    for flag in pyagram_flag.flags + (
                        pyagram_flag.frame.flags
                        if is_hidden and pyagram_flag.frame is not None
                        else []
                    )
                ],
            'self': pyagram_flag, # For postprocessing.
        }

    def encode_pyagram_frame(self, pyagram_frame):
        """
        """
        return {
            'type': 'function',
            'is_curr_element': pyagram_frame is self.state.program_state.curr_element,
            'name': repr(pyagram_frame),
            'parent':
                None
                if pyagram_frame.parent is None
                else repr(pyagram_frame.parent),
            'bindings': self.encode_mapping(
                pyagram_frame.bindings if pyagram_frame.shows_bindings else {},
                is_bindings=True,
            ),
            'return_value':
                self.encode_reference(pyagram_frame.return_value)
                if pyagram_frame.shows_return_value
                else None,
            'flags': [
                self.encode_pyagram_flag(flag)
                for flag in pyagram_frame.flags
            ],
        }

    def encode_banner_element(self, pyagram_flag, banner_element):
        """
        """
        if pyagram_flag.is_call_flag:
            code, keyword, binding_idx, unpacking_code = banner_element
            if binding_idx < len(pyagram_flag.banner_bindings):
                binding = pyagram_flag.banner_bindings[binding_idx]
                unpacking_type = enum.UnpackingTypes.identify_unpacking_type(unpacking_code)
                if unpacking_type is enum.UnpackingTypes.NORMAL:
                    keyless = keyword is None
                    bindings = self.encode_mapping(
                        (binding,) if keyless else {keyword: binding},
                        keyless=keyless,
                        is_bindings=True,
                    )
                elif unpacking_type is enum.UnpackingTypes.SINGLY_UNPACKED:
                    unpacked_binding = [*binding]
                    bindings = self.encode_mapping(
                        unpacked_binding,
                        keyless=True,
                        is_bindings=True,
                    )
                elif unpacking_type is enum.UnpackingTypes.DOUBLY_UNPACKED:
                    unpacked_binding = {**binding}
                    bindings = self.encode_mapping(
                        unpacked_binding,
                        is_bindings=True,
                    )
                else:
                    raise enum.UnpackingTypes.illegal_enum(unpacking_type)
            else:
                bindings = None
            return {
                'code': code,
                'n_cols':
                    2 * len(bindings) - 1 + sum(
                        binding['key'] is not None
                        for binding in bindings
                    )
                    if bindings is not None and len(bindings) > 0
                    else 1,
                'bindings': bindings,
            }
        elif pyagram_flag.is_comp_flag:
            return {
                'code': banner_element,
            }
        else:
            raise enum.PyagramFlagTypes.illegal_enum(pyagram_flag.flag_type)

    def encode_caught_exc_info(self, caught_exc_info):
        """
        """
        if caught_exc_info is None:
            return None
        else:
            type, value, traceback = caught_exc_info
            ex_cause = str(value)
            if len(ex_cause) > 0:
                ex_cause = f': {ex_cause}'
            lineno, _, _ = utils.decode_lineno(
                traceback.tb_lineno,
                max_lineno=self.num_lines,
            )
            return f'{type.__name__} (line {lineno}){ex_cause}'

    def encode_reference(self, object, *, is_bindings=False):
        """
        """
        object_type = enum.ObjectTypes.identify_raw_object_type(object)
        if object_type is enum.ObjectTypes.PRIMITIVE:
            return str(object) if is_bindings or type(object) is not str else repr(object)
        else:
            return self.object_id(object)

    def encode_object(self, object):
        """
        """
        object_type = enum.ObjectTypes.identify_tracked_object_type(object)
        if object_type is enum.ObjectTypes.FUNCTION:
            encoding = 'function'
            data = self.encode_function(object)
        elif object_type is enum.ObjectTypes.METHOD:
            encoding = 'method'
            data = self.encode_method(object)
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
        elif object_type is enum.ObjectTypes.USER_CLASS:
            encoding = 'class'
            data = self.encode_user_class(object)
        elif object_type is enum.ObjectTypes.BLTN_CLASS:
            encoding = 'class'
            data = self.encode_bltn_class(object)
        elif object_type is enum.ObjectTypes.INSTANCE:
            encoding = 'instance'
            data = self.encode_instance(object)
        elif object_type is enum.ObjectTypes.OTHER:
            encoding = 'other'
            data = self.encode_other(object)
        else:
            raise enum.ObjectTypes.illegal_enum(object_type)
        return {
            'encoding': encoding,
            'data': data,
        }

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
                    else self.encode_reference(parameter.default),
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

    def encode_method(self, object):
        """
        """
        return {
            'function': self.encode_reference(object.__func__),
            'instance': self.encode_reference(object.__self__),
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
                self.encode_reference(item)
                for item in object
            ],
        }

    def encode_mapping(self, object, *, keyless=False, is_bindings=False):
        """
        """
        if keyless:
            items = [
                {
                    'key': None,
                    'value': self.encode_reference(value),
                }
                for value in object
            ]
        else:
            items = [
                {
                    'key': self.encode_reference(key, is_bindings=is_bindings),
                    'value': self.encode_reference(value),
                }
                for key, value in object.items()
            ]
        if is_bindings:
            return items
        else:
            return {
                'type': type(object).__name__,
                'items': items,
            }

    def encode_iterator(self, object):
        """
        """
        iterable = utils.get_iterable(object)
        return None if iterable is None else {
            'object': self.encode_reference(iterable),
            'index': len(iterable) - object.__length_hint__(),
            'annotation':
                constants.ITERATOR_ANNOTATIONS[type(object)]
                if type(object) in constants.ITERATOR_ANNOTATIONS
                else None,
        }

    def encode_generator(self, object):
        """
        """
        results = object.results
        if results is not None:
            return_value, yield_from = results
        return {
            'name': object.generator.__name__,
            'frame': {
                'type': 'generator',
                'name': f'Frame {object.number}',
                'parent': repr(object.parent),
                'bindings': self.encode_mapping(
                    object.bindings,
                    is_bindings=True,
                ),
                'is_curr_element':
                    False
                    if object.curr_frame is None
                    else (object.curr_frame is self.state.program_state.curr_element),
                'return_value':
                    None
                    if results is None
                    else self.encode_reference(return_value),
                'from':
                    None
                    if results is None or yield_from is None
                    else self.encode_reference(yield_from),
                'flags': [],
            },
        }

    def encode_user_class(self, object):
        """
        """
        return {
            'type': 'class',
            'bltn': False,
            'is_curr_element': False,
            'name':
                object.frame.f_code.co_name
                if object.class_obj is None
                else object.class_obj.__name__,
            'parents':
                None # For postprocessing.
                if object.class_obj is None
                else self.encode_class_parents(object.class_obj),
            'bindings': self.encode_mapping(
                object.bindings,
                is_bindings=True,
            ),
            'return_value': None,
            'flags': [],
            'self': object, # For postprocessing.
        }

    def encode_bltn_class(self, object):
        """
        """
        return {
            'type': 'class',
            'bltn': True,
            'is_curr_element': False,
            'name': object.__name__,
            'parents': self.encode_class_parents(object),
            'bindings': self.encode_mapping(
                {},
                is_bindings=True,
            ),
            'return_value': None,
            'flags': [],
        }

    def encode_class_parents(self, class_obj):
        """
        """
        return [parent.__name__ for parent in class_obj.__bases__]

    def encode_instance(self, object):
        """
        """
        return {
            'type': 'instance',
            'is_curr_element': False,
            'name': type(object).__name__,
            'parent': type(object).__name__,
            'bindings': self.encode_mapping(
                object.__dict__,
                is_bindings=True,
            ),
            'return_value': None,
            'flags': [],
        }

    def encode_other(self, object):
        """
        """
        return repr(object)
