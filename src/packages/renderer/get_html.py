import flask

from . import templates

def get_html(template, **kwargs):
    return flask.Markup(flask.render_template_string(
        template,
        **kwargs,
        **globals(),
    )) # TODO: I'd love to `.strip` the whitespace here. Would that break things, like `x = 'a\nb'?)

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
        return 'TODO' # TODO: Encode an arrow with a <path></path> tag.
    else:
        raise TypeError()

def get_object_html(object_snapshot):
    return # TODO



# TODO: Get the memory state working.

# TODO: After clicking 'Draw Pyagram':
# TODO: (1) The button should stop working. Otherwise people will spam-click it and it'll just keep sending more requests to the server, which will just make things slower.
# TODO: (2) The button should change to say 'Drawing ...' or something like that.
# TODO: (3) The button's hover effect should go away.

# TODO: When the pyagram gets taller, your view should scroll to keep the curr_element in view.
