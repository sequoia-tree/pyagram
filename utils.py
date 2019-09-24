import gc
import inspect
import numbers
import types

# Primitive types: Compare with `==`.
PRIMITIVE_TYPES = (numbers.Number, str) # TODO: Complete (or verify it's complete)
# Referent types: Compare with `is`.
SINGLE_INSTANCE_TYPES = (None, NotImplemented, Ellipsis)
FUNCTION_TYPES = (types.FunctionType, types.MethodType) # TODO: Complete (or verify it's complete)

def is_primitive_type(object): # TODO: rename 'non-referent' as 'primitive'
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

def impute_flag_banners(snapshots, final_state):
    """
    <summary>

    :param snapshots:
    :return:
    """
    pass # TODO

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

def object_snapshot(object):
    """
    <summary> # snapshot a value (may be a referent type only)

    :param object:
    :return:
    """
    object_type = type(object)
    # if issubclass(type, ?):
    #     snapshot =
    # elif issubclass(object, ?):
    #     snapshot =
    # else:
    #     snapshot =
    #     # TODO: Get a snapshot of a generic object. Use gc.get_referents? Actually it might be safer to say "hey this is an unsupported type, sorry".
    snapshot = None # TODO
    return {
        'type': None if object_type in SINGLE_INSTANCE_TYPES else object_type.__name__,
        'object': snapshot,
        # TODO I think most built-in objects can be displayed as a sequence of boxes, or as one of 3 other preset structures. (Lists for example are a sequence of boxes since they're ordered and contain singleton elements.)
          # Sequential, singleton (tuple, list, etc): Sequence of connected boxes
          # Sequential, key-value (dictionary, etc):
          # Unordered, singleton ():
          # Unordered, key-value ():
          # Maybe sequential vs unordered doesn't change
    }
