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
        # TODO: Refactor this func -- it gets the id we use to track an obj
        raw_id = id(object)
        return self.state.memory_state.wrapped_obj_ids.get(raw_id, raw_id)

    def reference_snapshot(self, object, *, is_bindings=False):
        """
        """
        # TODO: Refactor this func
        if object is enum.ObjectTypes.UNKNOWN:
            return {} # TODO: I think this is obsolete now.
        object_type = enum.ObjectTypes.identify_object_type(object)
        if object_type is enum.ObjectTypes.PRIMITIVE:
            return self.encode_primitive(object, is_bindings=is_bindings)
        else:
            return self.object_id(object)

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

    def encode_primitive(self, object, *, is_bindings=False):
        """
        """
        return str(object) if is_bindings or type(object) is not str else repr(object)

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

    def encode_mapping(self, object, *, is_bindings=False, take=lambda key: True):
        """
        """
        items = [
            {
                'key': self.reference_snapshot(key, is_bindings=is_bindings),
                'value': self.reference_snapshot(value),
            }
            for key, value in object.items()
            if take(key)
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
            'object': self.reference_snapshot(iterable),
            'index': len(iterable) - object.__length_hint__(),
            'annotation':
                constants.ITERATOR_ANNOTATIONS[type(object)]
                if type(object) in constants.ITERATOR_ANNOTATIONS
                else None,
        }

    def encode_generator(self, object):
        """
        """
        latest_gen_frames = self.state.memory_state.latest_gen_frames
        generator_numbers = self.state.memory_state.generator_numbers
        generator_parents = self.state.memory_state.generator_parents
        frame_encoding = {
            'type': 'generator',
            'name': f'Frame {generator_numbers[object]}',
            'parent': repr(generator_parents[object]),
            'bindings': self.encode_mapping(
                inspect.getgeneratorlocals(object),
                is_bindings=True,
                take=utils.is_genuine_binding,
            ),
            'flags': [],
        }
        if object in latest_gen_frames:
            frame = latest_gen_frames[object]
            frame_encoding.update({
                'is_curr_element': frame is self.state.program_state.curr_element,
                'return_value':
                    self.reference_snapshot(frame.return_value)
                    if frame.shows_return_value
                    else None,
                'from': None if object.gi_yieldfrom is None else self.reference_snapshot(object.gi_yieldfrom),
            })
        else:
            frame_encoding.update({
                'is_curr_element': False,
                'return_value': None,
                'from': None,
            })
        return {
            'name': object.__name__,
            'frame': frame_encoding,
        }

    def encode_obj_class(self, object):
        """
        """
        return {
            'type': 'class',
            'is_curr_element': False,
            'name': object.frame.f_code.co_name,
            'parents': None, # Placeholder.
            'bindings': self.encode_mapping(
                object.bindings,
                is_bindings=True,
                take=lambda key: key not in pyagram_wrapped_object.PyagramClassFrame.HIDDEN_BINDINGS,
            ),
            'return_value': None,
            'from': None,
            'flags': [],
            'self': object, # For postprocessing.
        }

    def encode_obj_inst(self, object):
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
            'from': None,
            'flags': [],
        }

    def encode_exception_info(self, object):
        """
        """
        if object is None:
            return None
        else:
            type, value, traceback = object
            ex_cause = str(value)
            if len(ex_cause) > 0:
                ex_cause = f': {ex_cause}'
            lineno, _, _ = utils.decode_lineno(
                traceback.tb_lineno,
                max_lineno=self.num_lines,
            )
            return f'{type.__name__} (line {lineno}){ex_cause}'

    def encode_other(self, object):
        """
        """
        return repr(object)
