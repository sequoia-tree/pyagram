import copy

from . import get_html

def render_components(pyagram):
    """
    <description> # Give docstrings to the rest of the functions in this file and in get_html.py

    :param pyagram:
    :return:
    """
    snapshots = pyagram#pyagram.pop('snapshots')
    exception = False#pyagram.pop('exception')
    has_exception = exception is not None
    if has_exception:
        exception_snapshot = copy.deepcopy(snapshots[-1])
        snapshots.append(exception_snapshot)
    snapshots = [
        {
            'state': get_html.get_state_html(
                snapshot['program_state']['global_frame'],
                snapshot['memory_state'],
            ),
            'exception': None,
            'print_output': get_html.get_print_html(snapshot['print_output']),
            'curr_line_no': snapshot['program_state']['curr_line_no'],
        }
        for snapshot in snapshots
    ]
    # if has_exception:
    #     exception_snapshot = snapshots[-1]
    #     exception_snapshot['exception'] = get_html.get_exception_html(**exception)
    pyagram[:]=snapshots#pyagram['snapshots'] = snapshots
