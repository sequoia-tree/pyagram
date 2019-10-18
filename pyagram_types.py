import numbers
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
