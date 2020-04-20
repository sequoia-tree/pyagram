import gc
import inspect
import math
import types

from . import pyagram_types

INNER_CALL_LINENO = -1
OUTER_CALL_LINENO = -2
CLASS_DEFN_LINENO = -3

BANNER_FUNCTION_CODE = -1
BANNER_UNSUPPORTED_CODE = -2

def get_function(frame):
    """
    Get the function which was called todo todo

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

def assign_unique_code_object(function):
    """
    <summary>

    :param function:
    :return:
    """
    if isinstance(function, types.FunctionType):
        function = function
    elif isinstance(function, types.MethodType):
        function = function.__func__
    else:
        assert False
    function.__code__ = function.__code__.replace()

def get_variable_params(function):
    """
    <summary>

    :param function:
    """
    i = 0
    var_positional_index, var_positional_name, var_keyword_name = None, None, None
    for name, parameter in inspect.signature(function).parameters.items():
        if parameter.kind is inspect.Parameter.VAR_POSITIONAL:
            assert var_positional_index is None
            assert var_positional_name is None
            var_positional_index = i
            var_positional_name = name
        elif parameter.kind is inspect.Parameter.VAR_KEYWORD:
            assert var_keyword_name is None
            var_keyword_name = name
        i += 1
    return var_positional_index, var_positional_name, var_keyword_name

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

def pair_naturals(x, y, *, max_x):
    """
    """
    max_magnitude = 10 ** max(1, math.ceil(math.log10(max_x)))
    return max_magnitude * y + x

def unpair_naturals(pair, *, max_x):
    """
    """
    max_magnitude = 10 ** max(1, math.ceil(math.log10(max_x)))
    return pair % max_magnitude, pair // max_magnitude
