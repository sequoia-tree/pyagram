import gc
import inspect
import numbers
import types

# Primitive types: Compare with `==`.
PRIMITIVE_TYPES = (numbers.Number, str) # TODO: Complete (or verify it's complete)
# Referent types: Compare with `is`.
SINGLE_INSTANCE_TYPES = (None, NotImplemented, Ellipsis)
FUNCTION_TYPES = (types.FunctionType, types.MethodType) # TODO: Complete (or verify it's complete)

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

def value_str(object, function_parents):
    """
    <summary> # for displaying a value (may be a primitive or referent type)

    :param object:
    :param function_parents:
    :return:
    """
    if isinstance(object, FUNCTION_TYPES):
        name = object.__name__
        args = ', '.join(
            name if param.default is inspect.Parameter.empty else f'{name}={reference_str(param.default)}'
            for name, param in inspect.signature(object).parameters.items()
        ) # TODO: You've made sure to print default args. Good. But you have yet to implement logic for printing modifiers like *, **, \ (being added in 3.8), etc. Remember, there are several types of param in the Signature object: POSITIONAL_ONLY, POSITIONAL_OR_KEYWORD, VAR_POSITIONAL, KEYWORD_ONLY, and VAR_KEYWORD.
        parent = function_parents[object]
        return f'function {name}({args}) [p={repr(parent)}]'
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

def object_snapshot(object, function_parents):
    """
    <summary> # snapshot a value (may be a referent type only)

    :param object:
    :param function_parents:
    :return:
    """
    object_type = type(object)
    if issubclass(type, SINGLE_INSTANCE_TYPES):
        category = SINGLE_INSTANCE_TYPES
        snapshot = str(object)
    elif issubclass(object, FUNCTION_TYPES):
        category = FUNCTION_TYPES
        snapshot = '' # TODO: basically str(inspect.signature(object)) but you want the default args displayed too. if a default arg is a primitive, then just write it; if it's a referent type, then you want something like f(x, y=ptr to object, z=ptr to obj). it'd probably be easiest to serialize like {'function-name': str, 'parameters': [(str, *), (str, *), ...]} where "*" denotes the serialization of the default value if the param has one, or None if the param does not have one.
    # TODO: Test for a lot more classes of referent types. Eg lists, dicts, but also niche ones like range, dict_keys, etc. and of course don't forget about user-defined ones (but you can leave that one as just a TODO for now)!
    else:
        category = 'TODO' # TODO
        snapshot = 'TODO' # TODO: Get a snapshot of a generic object. Use gc.get_referents? Actually it might be safer to say "hey this is an unsupported type, sorry".
    return {
        'category': category,
        'type': None if object_type in SINGLE_INSTANCE_TYPES else object_type.__name__,
        'object': snapshot,
        # TODO I think most built-in objects can be displayed as a sequence of boxes, or as one of 3 other preset structures. (Lists for example are a sequence of boxes since they're ordered and contain singleton elements.)
          # Sequential, singleton (tuple, list, etc): Sequence of connected boxes
          # Sequential, key-value (dictionary, etc):
          # Unordered, singleton ():
          # Unordered, key-value ():
          # Maybe sequential vs unordered doesn't change
    }

def impute_flag_banners(snapshots, final_state):
    """
    <summary>

    :param snapshots:
    :return:
    """
    pass # TODO
