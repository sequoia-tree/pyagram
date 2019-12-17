from . import get_html

def render_components(pyagram):
    """
    <description> # Give docstrings to the rest of the functions in this file and in get_html.py

    :param pyagram:
    :return:
    """
    snapshots = pyagram.pop('snapshots')
    exception = pyagram.pop('exception')
    snapshots = [
        {
            'state': get_html.get_state_html(
                snapshot['program_state']['global_frame'],
                snapshot['memory_state'],
            ),
            'print_output': get_html.get_print_html(snapshot['print_output']),
            'curr_line_no': snapshot['program_state']['curr_line_no'], # TODO: Use this information.
        }
        for snapshot in snapshots
    ]
    if exception is not None:
        # TODO: Append a new snapshot which is identical except for the addition of a RED error message to the print_output.
        pass
    pyagram['snapshots'] = snapshots
