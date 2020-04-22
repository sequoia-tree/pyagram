import gc
import numbers
import types

# Primitive types: Compare with `==`.
PRIMITIVE_TYPES = (numbers.Number, str)
# Referent types: Compare with `is`.
FUNCTION_TYPES = (types.FunctionType, types.MethodType) # TODO: Finish -- once you get around to implementing class / instance functionality. (E.g. What about method-wrapper types like None.__str__? And check out type([].append) too!) BUT hold your rahi -- we might only want to track user-defined functions ... I mean, we don't step inside built-ins or even know what their parent frames are. Wrapper_descriptor and slot_wrapper? Maybe we should make method-wrappers and co. get drawn not in the style of functions, but in the style of objects? Oh and one more thing: how do you plan to visualize class functions vs. bound methods (e.g. A.f vs. A().f)?
BUILTIN_FUNCTION_TYPES =  (types.BuiltinFunctionType, types.BuiltinMethodType)
ORDERED_COLLECTION_TYPES = (list, tuple, str)
UNORDERED_COLLECTION_TYPES = (set, frozenset)
MAPPING_TYPES = (dict,) # TODO: Finish.
ITERATOR_TYPE_MAP = {
    type(iter([])): (list, None), # list_iterator
    type(iter(())): (tuple, None), # tuple_iterator
    type(iter('')): (str, None), # str_iterator
    type(iter(set())): (set, None), # set_iterator
    type(iter({}.keys())): (dict, 'keys'), # dict_keyiterator
    type(iter({}.values())): (dict, 'values'), # dict_valueiterator
    type(iter({}.items())): (dict, 'items'), # dict_itemiterator
    # type(iter(range(0))), # range_iterator # TODO: Works kinda differently than the others ...
}
ITERATOR_TYPES = tuple(ITERATOR_TYPE_MAP)
GENERATOR_TYPES = (types.GeneratorType,)
# TODO: Finish the above. Here are some ideas, but note they are not comprehensive ...
# TODO:     odict, odict_keys, ordereddict, etc.
# TODO:     types.MappingProxyType
# TODO:     OrderedDict
# TODO:     Counter
# TODO:     What about namedtuple classes / instances?
# TODO:     collections.*
# TODO:     map [the output of a call to `map`]
# TODO:     range ?
# TODO:     Various built-in Exceptions
# TODO: I think https://docs.python.org/3.8/library/types.html is a full list of types.

def is_primitive_type(object):
    """
    <summary>

    :param object: An arbitrary object.
    :return: Whether or not :object: is a primitive.
    """
    return isinstance(object, PRIMITIVE_TYPES)

def is_function_type(object):
    """
    <summary>

    :param object: An arbitrary object.
    :return: Whether or not :object: is a function.
    """
    return isinstance(object, FUNCTION_TYPES)

def is_builtin_type(object):
    """
    """
    return isinstance(object, BUILTIN_FUNCTION_TYPES)

def is_generator_type(object):
    """
    """
    return isinstance(object, GENERATOR_TYPES)

def get_iterable(iterator):
    """
    """
    iterable, iterable_type = None, ITERATOR_TYPE_MAP[type(iterator)][0]
    # TODO: This seems really sketch ... you're assuming, for example, that a list_iterator only has a reference to one list?
    for referent in gc.get_referents(iterator):
        if isinstance(referent, iterable_type):
            assert iterable is None
            iterable = referent
    return iterable
