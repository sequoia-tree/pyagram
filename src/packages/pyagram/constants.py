import types

USERCODE_FILENAME = 'main.py'

GENERIC_ERROR_MSG = """
A problem occurred while drawing the pyagram.
You can file an issue <a href="{issues}">here</a>. Please include your code in its entirety.
""".format(issues='https://github.com/sequoia-tree/pyagram/issues').strip('\n')

UNMODIFIED_LINENO = 0
INNER_CALL_LINENO = 1
INNER_COMP_LINENO = 2
FN_WRAPPER_LINENO = 3
RG_WRAPPER_LINENO = 4
PG_WRAPPER_LINENO = 5
CLASS_DEFN_LINENO = 6
CNTNR_COMP_LINENO = 7

NORMAL_ARG = 0
SINGLY_UNPACKED_ARG = 1
DOUBLY_UNPACKED_ARG = 2

HIDDEN_FLAG_CODE = -1

PRIMITIVE_TYPES = {
    # Primitives are values which should be compared with `==` instead of `is`.
    int,
    float,
    complex,
    bool,
    str,
}
FUNCTION_TYPES = {
    types.FunctionType,
}
METHOD_TYPES = {
    types.MethodType,
}
BUILTIN_TYPES = {
    types.BuiltinFunctionType,
    types.BuiltinMethodType,
}
ORDERED_COLLECTION_TYPES = {
    bytearray,
    bytes,
    list,
    tuple,
}
UNORDERED_COLLECTION_TYPES = {
    set,
    frozenset,
}
MAPPING_TYPES = {
    dict,
}
ITERATOR_TYPES = {
    type(iter([])): list,
    type(iter(())): tuple,
    type(iter('')): str,
    type(iter(set())): set,
    type(iter({}.keys())): dict,
    type(iter({}.values())): dict,
    type(iter({}.items())): dict,
}
ITERATOR_ANNOTATIONS = {
    type(iter({}.keys())): 'keys',
    type(iter({}.values())): 'values',
    type(iter({}.items())): 'items',
}
GENERATOR_TYPES = {
    types.GeneratorType,
}
# TODO: Finish the above. Here are some ideas, but note they are not comprehensive ...
# TODO:     odict, odict_keys, ordereddict, etc.
# TODO:     types.MappingProxyType
# TODO:     OrderedDict
# TODO:     Counter
# TODO:     What about namedtuple classes / instances?
# TODO:     collections.*
# TODO:     map (the output of a call to `map`)
# TODO:     range
# TODO:     Various built-in Exceptions
