import gc
import inspect
import types

from . import pyagram_types

INNER_CALL_LINENO = -1
OUTER_CALL_LINENO = -2

BANNER_FUNCTION_CODE = -1
BANNER_UNSUPPORTED_CODE = -2

def get_function(frame):
    """
    Get the function which was called  todo todo

    :param frame: The built-in :frame: object corresponding to some function call.
    :return: The function 
    """
    function = None
    for referrer in gc.get_referrers(frame.f_code):
        if pyagram_types.is_function_type(referrer):
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

def assign_unique_code_object(function):
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

def concatenate_adjacent_strings(elements):
    """
    <summary>

    :param elements:
    """
    # TODO: A decent practice problem to include in your texbtook, with a little modification.
    i = 0
    while i < len(elements) - 1:
        curr_elem = elements[i]
        next_elem = elements[i + 1]
        if isinstance(curr_elem, str) and isinstance(next_elem, str):
            elements[i] = ''.join((curr_elem, next_elem))
            del elements[i + 1]
        else:
            i += 1
