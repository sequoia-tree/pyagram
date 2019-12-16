from . import get_html

def render_components(pyagram):
    """
    <description> # Give docstrings to the rest of the functions in this file and in get_html.py

    :param pyagram:
    :return:
    """
    pyagram['snapshots'] = [
        {
            'curr_line_no': snapshot['program_state']['curr_line_no'],
            'state': get_html.get_state_html(
                snapshot['program_state']['global_frame'],
                snapshot['memory_state'],
            )
        }
        for snapshot in pyagram['snapshots']
    ]
    pyagram['exception'] = pyagram['exception'] # TODO: Convert the exception to HTML. Get the error message to display in a cute little red box, in the middle of the pyagram window.
