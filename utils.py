import gc
import inspect
import numbers
import types

# Primitive types: Compare with `==`.
PRIMITIVE_TYPES = (numbers.Number, str) # TODO: Complete (or verify it's complete)
# Referent types: Compare with `is`.
SINGLE_INSTANCE_TYPES = (None, Ellipsis, NotImplemented, Exception) #  TODO: And `Type` types? And what else?
FUNCTION_TYPES = (types.FunctionType, types.MethodType)

def is_primitive_type(object):
    """
    <summary>

    :param object:
    :return:
    """
    return isinstance(object, PRIMITIVE_TYPES)

def is_function_type(object):
    """
    <summary>

    :param object:
    :return:
    """
    return isinstance(object, FUNCTION_TYPES)

def enforce_one_function_per_code_object(function):
    """
    <summary>

    :param function:
    :return:
    """
    old_code = function.__code__
    new_code = types.CodeType(
        old_code.co_argcount,
        old_code.co_kwonlyargcount,
        old_code.co_nlocals,
        old_code.co_stacksize,
        old_code.co_flags,
        old_code.co_code,
        old_code.co_consts,
        old_code.co_names,
        old_code.co_varnames,
        old_code.co_filename,
        old_code.co_name,
        old_code.co_firstlineno,
        old_code.co_lnotab,
        old_code.co_freevars,
        old_code.co_cellvars,
    )
    function.__code__ = new_code

def get_function(frame):
    """
    <summary>

    :param frame:
    :return:
    """
    function = None
    for referrer in gc.get_referrers(frame.f_code):
        if isinstance(referrer, FUNCTION_TYPES):
            assert function is None, f'multiple functions refer to code object {frame.f_code}'
            function = referrer
    assert function is not None
    return function

def get_defaults(function):
    """
    <summary>

    :param function:
    :return:
    """
    parameters = inspect.signature(function).parameters.values()
    return [
        parameter.default
        for parameter in parameters
        if parameter.default is not inspect.Parameter.empty
    ]

def sort_parameter_bindings(bindings, function):
    """
    <summary>

    :param bindings:
    :param function:
    :return:
    """
    parameter_names = inspect.signature(function).parameters.keys()
    assert bindings.keys() == parameter_names
    sorted_parameter_bindings = {
        parameter_name: bindings[parameter_name]
        for parameter_name in parameter_names
    }
    bindings.clear()
    bindings.update(sorted_parameter_bindings)

def mapped_len(function):
    """
    <summary>

    :param function:
    :return:
    """
    return lambda object: len(function(object))

def get_binding(max_key_len, max_value_len):
    """
    <summary>

    :param max_key_len:
    :param max_value_len:
    :return:
    """
    return lambda key, value: f'|{key:>{max_key_len}}: {reference_str(value):<{max_value_len}}|'

def reference_str(object):
    """
    <summary> # for displaying a reference to a value (may be a primitive or referent type)

    :param object:
    :return:
    """
    return repr(object) if is_primitive_type(object) else f'*{id(object)}'

def object_str(object, memory_state):
    """
    <summary> # for displaying a value (may be a primitive or referent type)

    :param object:
    :param memory_state:
    :return:
    """
    if isinstance(object, FUNCTION_TYPES):
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
    if is_primitive_type(object):
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
    if issubclass(object, FUNCTION_TYPES):
        category = FUNCTION_TYPES
        snapshot = {
            'name': object.__name__,
            'parameters': [
                {
                    'name': str(parameter) if parameter.default is inspect.Parameter.empty else str(parameter).split('=', 1)[0],
                    'default': None if parameter.default is inspect.Parameter.empty else reference_snapshot(parameter.default, memory_state)
                }
                for parameter in inspect.signature(object).parameters.values()
            ],
            'parent': f'[p={repr(memory_state.function_parents[object])}]',
        }
    elif issubclass(type, SINGLE_INSTANCE_TYPES):
        category = SINGLE_INSTANCE_TYPES
        snapshot = str(object)
        # TODO: More generalizable: Right now you're specifying which objects don't merit a 'label' -- namely, those in SINGLE_INSTANCE_TYPES. But you can't get all of them! There's always stuff like inspect.Parameter.empty that's way too niche, and the user can even make their own. Instead, just give everything a label. Then, note that the label for `None`, `NotImplemented`, etc is just "None", "NotImplemented", etc. -- so you can simply omit the 'object' instead of the 'label'. Really you only need the 'object' field for complex things that contain pointers to other functions, like containers or functions.
    # TODO: Add more elifs for more classes of referent types. Eg lists, dicts, but also niche ones like range, dict_keys, etc. and of course don't forget about user-defined ones (but you can leave that one as just a TODO for now) (not just normal classes, but also abstract classes and instances)!
    else:
        category = 'TODO' # TODO
        snapshot = 'TODO' # TODO: Get a snapshot of a generic object. Use gc.get_referents? Actually it might be safer to say "hey this is an unsupported type, sorry".
        # TODO: Better idea: As a catch-all, use your method of OOP diagrams from your textbook. But first write down a few elifs to catch unsupported things like async and coroutines?
    return {
        'category': category, # So the de-serializer knows how to decode `object`, since it varies depending on which category it's in.
        'label': None if object_type in SINGLE_INSTANCE_TYPES else object_type.__name__,
        'object': snapshot,
        # TODO I think most built-in objects can be displayed as a sequence of boxes, or as one of 3 other preset structures. (Lists for example are a sequence of boxes since they're ordered and contain singleton elements.)
          # Sequential, singleton (tuple, list, etc): Sequence of connected boxes
          # Sequential, key-value (dictionary, etc):
          # Unordered, singleton ():
          # Unordered, key-value ():
          # Maybe sequential vs unordered doesn't change
          # TODO: Draw a dict like a list, but instead of a 1xN box it's a 2xN box for key / vals?
    }

def impute_flag_banners(snapshots, final_state):
    """
    <summary>

    :param snapshots:
    :return:
    """
    pass # TODO
