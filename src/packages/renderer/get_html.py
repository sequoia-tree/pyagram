import flask

from . import templates

def get_html(template, component_snapshot):
    return flask.render_template_string(
        template,
        this=component_snapshot,
        **component_snapshot,
        **globals(),
    )

def get_element_html(element_snapshot):
    return get_html(templates.ELEMENT_TEMPLATE, element_snapshot)

def get_flag_html(flag_snapshot):
    return get_html(templates.FLAG_TEMPLATE, flag_snapshot)

def get_frame_html(frame_snapshot):
    return get_html(templates.FRAME_TEMPLATE, frame_snapshot)

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

def get_object_html(object_snapshot):
    return # TODO
