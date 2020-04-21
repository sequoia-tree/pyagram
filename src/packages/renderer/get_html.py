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

def get_component_html(template, component_snapshot, **kwargs):
    return get_html(
        template,
        this=component_snapshot,
        **component_snapshot,
        **kwargs,
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
    return get_component_html(templates.FRAME_TEMPLATE, frame_snapshot, frame_type='function')

def get_reference_html(reference_snapshot, *, monospace=True):
    if isinstance(reference_snapshot, dict):
        return get_html(
            templates.META_REFERENCE_TEMPLATE,
            **reference_snapshot,
        )
    elif isinstance(reference_snapshot, str):
        return get_html(
            templates.PLAINTEXT_TEMPLATE,
            text=reference_snapshot,
            monospace=monospace,
        )
    elif isinstance(reference_snapshot, int):
        return get_html(
            templates.POINTER_TEMPLATE,
            id=reference_snapshot,
        )
    else:
        raise TypeError()

def get_object_html(object_snapshot):
    return get_component_html(templates.OBJECT_TEMPLATE, object_snapshot)

def get_object_body_html(object_encoding):
    encoding = object_encoding['encoding']
    object_snapshot = object_encoding['object']
    if encoding == 'function':
        return get_component_html(templates.FUNCTION_TEMPLATE, object_snapshot)
    elif encoding == 'builtin_function':
        return get_component_html(templates.BUILTIN_FUNCTION_TEMPLATE, object_snapshot)
    elif encoding == 'ordered_collection':
        return get_component_html(templates.ORDERED_COLLECTION_TEMPLATE, object_snapshot)
    elif encoding == 'unordered_collection':
        return get_component_html(templates.UNORDERED_COLLECTION_TEMPLATE, object_snapshot)
    elif encoding == 'mapping':
        return get_component_html(templates.MAPPING_TEMPLATE, object_snapshot)
    elif encoding == 'iterator':
        return get_component_html(templates.ITERATOR_TEMPLATE, object_snapshot)
    elif encoding == 'generator':
        return get_component_html(templates.FRAME_TEMPLATE, object_snapshot, frame_type='generator')
    elif encoding == 'class_frame':
        return get_component_html(templates.FRAME_TEMPLATE, object_snapshot, frame_type='class')
    elif encoding == 'object_dict':
        return get_component_html(templates.FRAME_TEMPLATE, object_snapshot, frame_type='instance')
    elif encoding == 'object_repr':
        return get_component_html(templates.OBJECT_REPR_TEMPLATE, object_snapshot)
    else:
        assert False

def get_lambda_html(lambda_snapshot):
    return get_component_html(templates.LAMBDA_TEMPLATE, lambda_snapshot)

def get_parameter_html(parameter_snapshot):
    return get_component_html(templates.PARAMETER_TEMPLATE, parameter_snapshot)

def get_parent_frame_html(parents_snapshot, *, monospace=False):
    return get_html(
        templates.PARENT_FRAME_TEMPLATE,
        parents=[
            get_reference_html(parent_reference, monospace=monospace)
            for parent_reference in parents_snapshot
        ],
    )

def get_print_html(print_output, **kwargs):
    return get_html(
        templates.PRINT_TEMPLATE,
        print_output=print_output,
        **kwargs,
    )

def get_exception_html(type, value, lineno):
    if 0 < len(value):
        return get_print_html([f'{type}: {value}'], is_exception=True)
    else:
        return get_print_html([type], is_exception=True)

# TODO: Instead of having layout.scss, just use jQuery to get the height of the editor + scrollbar, and set that element to have min-height: X + "px".

# TODO: When the pyagram gets taller, your view should scroll to keep the curr_element in view.
