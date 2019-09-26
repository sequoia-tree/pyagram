import collections.abc
import gc
import inspect
import numbers
import re
import types

# Primitive types: Compare with `==`.
PRIMITIVE_TYPES = (numbers.Number, str) # TODO: Finish.
# Referent types: Compare with `is`.
FUNCTION_TYPES = (types.FunctionType, types.MethodType) # TODO: Finish -- once you get around to implementing class / instance functionality. (E.g. What about method-wrapper types like None.__str__? And check out type([].append) too!) BUT hold your rahi -- we might only want to track user-defined functions ... I mean, we don't step inside built-ins or even know what their parent frames are. Wrapper_descriptor and slot_wrapper? Maybe we should make method-wrappers and co. get drawn not in the style of functions, but in the style of objects? Oh and one more thing: how do you plan to visualize class functions vs. bound methods (e.g. A.f vs. A().f)?
ORDERED_COLLECTION_TYPES = (list, tuple, str)
UNORDERED_COLLECTION_TYPES = (set, frozenset)
MAPPING_TYPES = (dict, types.MappingProxyType) # TODO: Finish.
ITERATOR_TYPES = () # TODO: Finish.
GENERATOR_TYPES = (types.GeneratorType,)
# TODO: Finish the above. Here are some ideas, but note they are not comprehensive ...
# TODO:     odict, odict_keys, ordereddict, etc.
# TODO:     OrderedDict
# TODO:     Counter
# TODO:     What about namedtuple classes / instances?
# TODO:     collections.*
# TODO:     list_iterator
# TODO:     tuple_iterator
# TODO:     str_iterator
# TODO:     set_iterator
# TODO:     dict_keyiterator
# TODO:     dict_valueiterator
# TODO:     dict_itemiterator
# TODO:     range_iterator
# TODO:     map [the output of a call to `map`; a kind of iterator]
# TODO:     Various built-in Exceptions

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
        if is_function_type(referrer):
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
    if object_type in FUNCTION_TYPES:
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
            'parent': f'[p={repr(memory_state.function_parents[object])}]',
        }
    elif object_type in ORDERED_COLLECTION_TYPES:
        encoding = 'ordered-collection'
        snapshot = [
            reference_snapshot(item, memory_state)
            for item in object
        ]
    elif object_type in UNORDERED_COLLECTION_TYPES:
        encoding = 'unordered-collection'
        snapshot = [
            reference_snapshot(item, memory_state)
            for item in object
        ]
    elif object_type in MAPPING_TYPES:
        encoding = 'mapping'
        snapshot =  [
            [reference_snapshot(key, memory_state), reference_snapshot(value, memory_state)]
            for key, value in object.items()
        ]
    elif object_type in ITERATOR_TYPES:
        encoding = 'iterator'
        snapshot = NotImplemented # TODO
    elif object_type in GENERATOR_TYPES:
        encoding = 'generator'
        snapshot = NotImplemented # TODO
    else:
        if hasattr(object, '__dict__'):
            encoding = 'object-frame'
            snapshot = NotImplemented # TODO
            # TODO: The `snapshot` should be a generic OOP object-frame, as in your textbook. (The object frame's bindings should be `object.__dict__`.)
            # TODO: If `object_type is Type` then write "class X [p=Y]", else "instance X [p=Y]".
            # TODO: Some objects have a *lot* of items in their `.__dict__`. You have a few options:
              # (*) Make it an option [default ON] to render the contents in object frames.
              # (*) Limit the size of each object frame, but make the contents scrollable on the site.
              # (*) Include a button next to each object frame, which you can click to toggle whether to render the contents of that particular object frame.
        else:
            encoding = 'object-repr'
            snapshot = repr(object)
    return {
        'encoding': encoding, # So the decoder knows the structure of `snapshot`.
        'label': object_type.__name__,
        'object': snapshot,
    }

def interpolate_flag_banners(snapshots, final_state):
    """
    <summary>

    :param snapshots:
    :return:
    """
    pass # TODO

def split_function_call(code_lines, line_no, col_offset):
    """
    <summary>

    :param code:
    :param line_no:
    :param col_offset:
    :return:
    """
    # TODO: For parentheses matching, regex won't work: you're dealing with nested structures and need to use recursion. Do you basically need to watch out for single quotes, double quotes, triple single quotes, and triple double quotes, and when you see any such (non-escaped) construct just skip until the next matching (non-escaped) construct?
    # TODO: Fortunately I don't think we need additional logic for f-strings.
    # TODO: You can use regex to eliminate strings, since it's impossible to nest strings unless the inner ones have escape characters delimiting them.
    # TODO: Pass in the CallWrapper's self.code_lines for code_lines, and `lineno - 1` for line_no (because lineno is 1-indexed and I'm using 0-indexed here).
    
    pass # TODO: Before giving the code to the CallWrapper, use regex to get a list [(start, end), (start, end), ...] where each "start" or "end" respectively denotes the (line_no, col_offset) where a string starts or ends. Then in this function you can just jump over all the strings super easy and not worry about them! See `find_strings` above.

    # TODO: Keep track of each index where there's a legit (ie non-string) open-paren and each index where there's a legit close-paren. Stop when you see a close-paren that is not immediately followed by an open paren.

def find_string_indices(code):
    """
    <summary>
    
    :code:
    :return:
    """

    # You can't just use re.findall to search for ', ", ''', and """ strings individually and then merge together your findings. Consider the input '\'''': it's really the strings ('\'', '') so after the last quote you're OUT of a string. However if you were to look for triple quotes individually you'd START reading on the 4th quote, and so you'd think your IN a string (a triple-quote delimited string) after the last quote. So it is necessary to do a loop, and repeatedly do re.search, rather than using re.findall.
    
    # You must account for `'''` and `"""` explicitly; you can't just rely on the `'` pattern to find `'''` patterns and the `"` pattern to find `"""` patterns; they're fundamentally different. For example try `" \""" "` vs `""" \""" """`.

    string_indices = []
    while True:
        next_triplequote_indices = find_first_delimited_substring_indices(code, '"""', "'''")
        next_singlequote_indices = find_first_delimited_substring_indices(code, '"', '"')
        has_triplequote_match = next_triplequote_indices is not None
        has_singlequote_match = next_singlequote_indices is not None
        if has_triplequote_match or has_singlequote_match:
            # Triple-quotes take precedence over single-quotes. If you see `'''` then make sure it's processed as the start of a '''-string, instead of `''` followed by the start of a '-string.
            if has_triplequote_match and next_triplequote_indices[0] == next_singlequote_indices[0]:
                next_indices = next_triplequote_indices
            else:
                next_indices = next_singlequote_indices
                # As a sanity check, make sure ' and " -delimited strings aren't multi-line.
                assert all(
                    '\n' != code[i]
                    for i in range(next_indices[0], next_indices[1])
                )
            string_indices.append(next_indices)
            code = code[next_indices[1]:]
        else:
            break
    return string_indices
    # TODO: CHECK / TEST THIS

def find_first_delimited_substring_indices(text, *delimiters):
    """
    <summary>

    :text:
    :delimiters:
    :return:
    """
    if len(text) == 0:
        return None
    else:
        start_pattern = lambda delimiter: fr'{delimiter}(?:{delimiter}|.*?[^\\]{delimiter})'
        later_pattern = lambda delimiter: fr'[^\\]{delimiter}(?:{delimiter}|.*?[^\\]{delimiter})'
        starting_match = re.match(start_pattern(text[0]), text) if text[0] in delimiters else None
        if starting_match is None:
            matches = {
                re.search(later_pattern(delimiter), text)
                for delimiter in delimiters
            }
            matches.discard(None)
            matches = {(match.start() + 1, match.end()) for match in matches}
            return min(matches) if matches else None
        else:
            return starting_match.span()
    # TODO: CHECK / TEST THIS
