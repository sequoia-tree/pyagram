import gc
import inspect
import types

NON_REFERENT_TYPES = (int, float, str, bool)

def reference_snapshot(object, memory_state):
    """
    <summary> # snapshot a reference to a value (may be a referent type or not)

    :param object:
    :param memory_state:
    :return:
    """
    if is_referent_type(object):
        return memory_state.object_ids[id(object)]
    else:
        return repr(object) if isinstance(object, str) else str(object)

def object_snapshot(object):
    """
    <summary> # snapshot a value (may be a referent type or not)

    :param object:
    :return:
    """
    return {
        'type': type(object).__name__,
        'object': None, # TODO: Get a JSON-style serialization of the object! Perhaps use gc.get_referents?
    }

def is_referent_type(object):
    """
    <summary>

    :param object:
    :return:
    """
    return not isinstance(object, NON_REFERENT_TYPES)

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
        if isinstance(referrer, types.FunctionType):
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
