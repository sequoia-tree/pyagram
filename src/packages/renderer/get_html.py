import flask

from . import templates

def get_html(template, **kwargs):
    return flask.Markup(flask.render_template_string(
        ''.join((
            template_line.strip()
            for template_line in template.split('\n')
        )),
        **kwargs,
        **globals(),
    ))

def get_component_html(template, component_snapshot):
    return get_html(
        template,
        this=component_snapshot,
        **component_snapshot,
    )

def get_state_html(global_frame_snapshot, memory_state_snapshot):
    return get_html(
        templates.STATE_TEMPLATE,
        global_frame=global_frame_snapshot,
        memory_state=memory_state_snapshot,
    )

def get_element_html(element_snapshot):
    return get_component_html(templates.ELEMENT_TEMPLATE, element_snapshot)

def get_flag_html(flag_snapshot):
    return get_component_html(templates.FLAG_TEMPLATE, flag_snapshot)

def get_frame_html(frame_snapshot):
    return get_component_html(templates.FRAME_TEMPLATE, frame_snapshot)

def get_reference_html(reference_snapshot):
    if isinstance(reference_snapshot, list):
        assert len(reference_snapshot) == 2
        return get_html(
            templates.LINK_TEMPLATE,
            text=reference_snapshot[0],
            link=reference_snapshot[1],
        )
    elif isinstance(reference_snapshot, str):
        return reference_snapshot
    elif isinstance(reference_snapshot, int):
        # TODO: Encode an arrow with a <path></path> tag.
        # TODO: Point to the element with id `object-i`.
        return 'TODO'
    else:
        raise TypeError()

def get_object_html(object_encoding):
    encoding = object_encoding['encoding']
    object_snapshot = object_encoding['object']
    if encoding == 'function':
        # TODO: Get rid of the weird spaces after the '(' and before the ')'.
        # TODO: Make the parameters comma-separated.
        # TODO: Check that it works well with default values.
        # TODO: A function with a really long name should make the window scroll horizontally. It should not wrap to a new line.
        return get_component_html(templates.FUNCTION_TEMPLATE, object_snapshot)
    elif encoding == 'ordered_collection':
        return get_component_html(templates.ORDERED_COLLECTION_TEMPLATE, object_snapshot)
    elif encoding == 'unordered_collection':
        return get_component_html(templates.UNORDERED_COLLECTION_TEMPLATE, object_snapshot)
    elif encoding == 'mapping':
        return get_component_html(templates.MAPPING_TEMPLATE, object_snapshot)
    elif encoding == 'iterator':
        return get_component_html(templates.ITERATOR_TEMPLATE, object_snapshot)
    elif encoding == 'generator':
        return get_component_html(templates.GENERATOR_TEMPLATE, object_snapshot)
    elif encoding == 'object_frame':
        return get_component_html(templates.OBJECT_FRAME_TEMPLATE, object_snapshot)
    elif encoding == 'object_repr':
        return get_component_html(templates.OBJECT_REPR_TEMPLATE, object_snapshot)
    else:
        assert False

def get_parameter_html(parameter_snapshot):
    return get_component_html(templates.PARAMETER_TEMPLATE, parameter_snapshot)

def get_parent_frame_html(parent_frame_name):
    return get_html(
        templates.PARENT_FRAME_TEMPLATE,
        parent_frame_name=parent_frame_name,
    )

# TODO: Next up, get the arrows to show up!

# TODO: Draw the memory state.
# TODO: The arrows can be a color other than black, to make them easy to see.
# TODO: The arrows can also become red on hover, to make them easy to see.
# TODO: Right now you have two columns in the STATE_TEMPLATE. Perhaps you should have three: one for the flags and frames, one for object frames, and one for other objects (functions, lists, etc.)?

# TODO: After clicking 'Draw Pyagram':
# TODO: (1) The button should stop working. Otherwise people will spam-click it and it'll just keep sending more requests to the server, which will just make things slower.
# TODO: (2) The button should change to say 'Drawing ...' or something like that.
# TODO: (3) The button's hover effect should go away.

# TODO: When the pyagram gets taller, your view should scroll to keep the curr_element in view.
