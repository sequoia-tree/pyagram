import inspect
import re

from . import pyagram_types

UNKNOWN_REFERENCE_TEXT = '<?>'
GITHUB_ISSUES_URL = 'https://github.com/sequoia-tree/pyagram/issues'

class Encoder:
    """
    """

    def __init__(self):
        pass

    def reference_snapshot(self, object, memory_state):
        """
        <summary> # snapshot a reference to a value (may be a primitive or referent type)

        :param object:
        :param memory_state:
        :return:
        """
        if object is None and memory_state is None: # TODO: If this is the only place memory_state gets used in this function, then you should replace the memory_state param with simply a boolean param is_unknown=False or something like that. Or if you like, you could do something that's more extensible to other URLs just in case you ever want to make use of that functionality.
            return [UNKNOWN_REFERENCE_TEXT, GITHUB_ISSUES_URL] # hyperlink: [text, URL]
        elif pyagram_types.is_primitive_type(object):
            return repr(object) if isinstance(object, str) else str(object)
        else:
            return id(object)

    def object_snapshot(self, object, memory_state):
        """
        <summary> # snapshot a value (may be a referent type only)

        :param object:
        :param memory_state:
        :return:
        """
        object_type = type(object)
        if object_type in pyagram_types.FUNCTION_TYPES:
            is_lambda = object.__name__ == '<lambda>'
            if is_lambda:
                for parameter_name in inspect.signature(object).parameters.keys():
                    match = re.match(r'^__pyagram_lambda_(\d+)_(\d+)$', parameter_name)
                    if match is not None:
                        lineno = match.group(1)
                        number = match.group(2)
            encoding = 'function'
            snapshot = {
                'name': object.__name__,
                'lambda_id':
                    {
                        'lineno': lineno,
                        'number': number,
                    }
                    if is_lambda
                    else None,
                'parameters': [
                    {
                        'name': str(parameter) if parameter.default is inspect.Parameter.empty else str(parameter).split('=', 1)[0],
                        'default': None if parameter.default is inspect.Parameter.empty else self.reference_snapshot(parameter.default, memory_state),
                    }
                    for parameter in inspect.signature(object).parameters.values()
                ],
                'parent': repr(memory_state.function_parents[object]),
            }
        elif object_type in pyagram_types.ORDERED_COLLECTION_TYPES:
            encoding = 'ordered_collection'
            snapshot = {
                'elements': [
                    self.reference_snapshot(item, memory_state)
                    for item in object
                ],
            }
        elif object_type in pyagram_types.UNORDERED_COLLECTION_TYPES:
            encoding = 'unordered_collection'
            snapshot = {
                'elements': [
                    self.reference_snapshot(item, memory_state)
                    for item in object
                ],
            }
        elif object_type in pyagram_types.MAPPING_TYPES:
            encoding = 'mapping'
            snapshot =  {
                'items': [
                    [self.reference_snapshot(key, memory_state), self.reference_snapshot(value, memory_state)]
                    for key, value in object.items()
                ],
            }
        elif object_type in pyagram_types.ITERATOR_TYPES:
            encoding = 'iterator'
            snapshot = NotImplemented # TODO
        elif object_type in pyagram_types.GENERATOR_TYPES:
            encoding = 'generator'
            snapshot = NotImplemented # TODO
        else:
            if hasattr(object, '__dict__'):
                encoding = 'object_frame'
                snapshot = NotImplemented # TODO
                # TODO: The `snapshot` should be a generic OOP object-frame, as in your textbook. (The object frame's bindings should be `object.__dict__`.)
                # TODO: If `object_type is Type` then write "class X [p=Y]", else "instance X [p=Y]".
                # TODO: Some objects have a *lot* of items in their `.__dict__`. You have a few options:
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
