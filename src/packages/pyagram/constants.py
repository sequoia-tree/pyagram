import fractions
import types

USERCODE_FILENAME = 'main.py'

UNMODIFIED_LINENO = 0
FN_WRAPPER_LINENO = 1
RG_WRAPPER_LINENO = 2
INNER_CALL_LINENO = 3
OUTER_CALL_LINENO = 4
CLASS_DEFN_LINENO = 5
CNTNR_COMP_LINENO = 6

NORMAL_ARG = 0
SINGLY_UNPACKED_ARG = 1
DOUBLY_UNPACKED_ARG = 2

HIDDEN_FLAG_CODE = -1

PRIMITIVE_TYPES = {
    # Primitives are values which should be compared with `==` instead of `is`.
    int,
    float,
    complex,
    fractions.Fraction,
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
    list,
    tuple,
    str,
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
