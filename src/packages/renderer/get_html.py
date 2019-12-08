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
        return flask.render_template_string(
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



# TODO: (1) Get the flag banners working.
# TODO: (2) Get the curr-element working. See take_snapshot in trace.py.
# TODO: (3) Get the memory state working.



def get_memory_state_html(memory_state_snapshot):
    return # TODO

def get_object_html(object_snapshot):
    return # TODO
