import gc
import inspect
import math
import re
import types

from . import constants
from . import enum

def pair_naturals(x, y, *, max_x):
    """
    """
    max_magnitude = 10 ** math.ceil(math.log10(max_x + 1))
    return max_magnitude * y + x

def unpair_naturals(pair, *, max_x):
    """
    """
    max_magnitude = 10 ** math.ceil(math.log10(max_x + 1))
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
        # TODO: What about slot wrappers and other atypical callables?
        # TODO: Bound methods (i.e. ObjectTypes.METHOD) don't contain a ref to the code. They refer to the function (via .__func__), which refers to the code. If a bound method opens a frame, this will return the .__func__ of that bound method -- which should be fine.
        if enum.ObjectTypes.identify_raw_object_type(referrer) is enum.ObjectTypes.FUNCTION:
            assert function is None, f'multiple functions refer to code object {frame.f_code}'
            function = referrer
    return function

def get_generator(frame):
    """
    """
    generator = None
    for referrer in gc.get_referrers(frame):
        if inspect.isgenerator(referrer) and referrer.gi_frame is frame:
            assert generator is None, f'multiple generators refer to frame object {frame}'
            generator = referrer
    return generator

def assign_unique_code_object(function):
    """
    """
    function.__code__ = function.__code__.replace()

def get_defaults(function):
    """
    """
    parameters = inspect.signature(function).parameters.values()
    return [
        parameter.default
        for parameter in parameters
        if parameter.default is not inspect.Parameter.empty
    ]

def get_iterable(iterator):
    """
    """
    iterable, iterable_type = None, constants.ITERATOR_TYPES[type(iterator)]
    for referent in gc.get_referents(iterator):
        if type(referent) is iterable_type:
            assert iterable is None
            iterable = referent
    return iterable

def is_genuine_binding(variable):
    """
    """

    # For comprehensions and generator comprehensions.
    # Their frames sometimes has implicit variables named `.0`, `.1`, etc.

    return re.fullmatch(r'\.\d+', variable) is None
