import fractions
import types

UNMODIFIED_LINENO = 0
INNER_CALL_LINENO = 1
OUTER_CALL_LINENO = 2
CLASS_DEFN_LINENO = 3

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
    type(iter([])),
    type(iter(())),
    type(iter('')),
    type(iter(set())),
    type(iter({}.keys())),
    type(iter({}.values())),
    type(iter({}.items())),
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
