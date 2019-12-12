import inspect

from . import pyagram_types

UNKNOWN_REFERENCE_TEXT = '<?>'
GITHUB_ISSUES_URL = 'https://github.com/sequoia-tree/pyagram/issues'

def reference_str(object):
    """
    <summary> # for displaying a reference to a value (may be a primitive or referent type)

    :param object:
    :return:
    """
    return repr(object) if pyagram_types.is_primitive_type(object) else f'*{id(object)}'

def object_str(object, memory_state):
    """
    <summary> # for displaying a value (may be a primitive or referent type)

    :param object:
    :param memory_state:
    :return:
    """
    if isinstance(object, pyagram_types.FUNCTION_TYPES):
        name = object.__name__
        parameters = inspect.signature(object)
        parent = memory_state.function_parents[object]
        return f'function {name}{parameters} [p={repr(parent)}]'
    else:
        return repr(object)

def reference_snapshot(object, memory_state):
    """
    <summary> # snapshot a reference to a value (may be a primitive or referent type)

    :param object:
    :param memory_state:
    :return:
    """
    if object is None and memory_state is None:
        return [UNKNOWN_REFERENCE_TEXT, GITHUB_ISSUES_URL] # hyperlink: [text, URL]
    elif pyagram_types.is_primitive_type(object):
        return repr(object) if isinstance(object, str) else str(object)
    else:
        return memory_state.object_ids[id(object)]

def object_snapshot(object, memory_state):
    """
    <summary> # snapshot a value (may be a referent type only)

    :param object:
    :param memory_state:
    :return:
    """
    object_type = type(object)
    if object_type in pyagram_types.FUNCTION_TYPES:
        encoding = 'function'
        snapshot = {
            'name': object.__name__,
            'parameters': [
                {
                    'name': str(parameter) if parameter.default is inspect.Parameter.empty else str(parameter).split('=', 1)[0],
                    'default': None if parameter.default is inspect.Parameter.empty else reference_snapshot(parameter.default, memory_state),
                }
                for parameter in inspect.signature(object).parameters.values()
            ],
            'parent': repr(memory_state.function_parents[object]),
        }
    elif object_type in pyagram_types.ORDERED_COLLECTION_TYPES:
        encoding = 'ordered_collection'
        snapshot = {
            'elements': [
                reference_snapshot(item, memory_state)
                for item in object
            ],
        }
    elif object_type in pyagram_types.UNORDERED_COLLECTION_TYPES:
        encoding = 'unordered_collection'
        snapshot = {
            'elements': [
                reference_snapshot(item, memory_state)
                for item in object
            ],
        }
    elif object_type in pyagram_types.MAPPING_TYPES:
        encoding = 'mapping'
        snapshot =  {
            'items': [
                [reference_snapshot(key, memory_state), reference_snapshot(value, memory_state)]
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
