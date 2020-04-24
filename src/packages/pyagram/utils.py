import gc
import inspect
import math

from . import constants
from . import pyagram_types

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

def encode_lineno(lineno, natural, is_lambda, *, max_lineno):
    """
    """
    pair = pair_naturals(lineno, natural, max_x=max_lineno)
    return pair if is_lambda else -pair

def decode_lineno(lineno, *, max_lineno):
    """
    """
    if lineno < 0:
        (lineno, step_code), lambda_number = unpair_naturals(-lineno, max_x=max_lineno), 0
    elif max_lineno < lineno:
        (lineno, lambda_number), step_code = unpair_naturals(lineno, max_x=max_lineno), constants.UNMODIFIED_LINENO
    else:
        lineno, step_code, lambda_number = lineno, constants.UNMODIFIED_LINENO, 0
    return lineno, step_code, lambda_number

def get_function(frame):
    """
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
    """
    parameters = inspect.signature(function).parameters.values()
    return [
        parameter.default
        for parameter in parameters
        if parameter.default is not inspect.Parameter.empty
    ]

def get_variable_params(function):
    """
    """
    var_positional_index, var_positional_name, var_keyword_name = None, None, None
    for i, (name, parameter) in enumerate(inspect.signature(function).parameters.items()):
        if parameter.kind is inspect.Parameter.VAR_POSITIONAL:
            assert var_positional_index is None
            assert var_positional_name is None
            var_positional_index = i
            var_positional_name = name
        elif parameter.kind is inspect.Parameter.VAR_KEYWORD:
            assert var_keyword_name is None
            var_keyword_name = name
    return var_positional_index, var_positional_name, var_keyword_name

def concatenate_adjacent_strings(elements):
    """
    """
    i = 0
    while i < len(elements) - 1:
        curr_elem = elements[i]
        next_elem = elements[i + 1]
        if isinstance(curr_elem, str) and isinstance(next_elem, str):
            elements[i] = ''.join((curr_elem, next_elem))
            del elements[i + 1]
        else:
            i += 1







def is_generator_frame(pyagram_frame):
    """
    """
    return inspect.isgeneratorfunction(pyagram_frame.function)












import types


BANNER_FUNCTION_CODE = -1
BANNER_UNSUPPORTED_CODE = -2

def assign_unique_code_object(function):
    """
    """
    if isinstance(function, types.FunctionType):
        function = function
    elif isinstance(function, types.MethodType):
        function = function.__func__
    else:
        assert False
    function.__code__ = function.__code__.replace()
