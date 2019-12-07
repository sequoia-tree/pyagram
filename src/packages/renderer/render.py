from . import get_html

def render_components(snapshots):
    """
    <description> # Give docstrings to the rest of the functions in this file and in get_html.py

    :param snapshots:
    :return:
    """
    for snapshot in snapshots:
        program_state = snapshot.pop('program_state')
        memory_state = snapshot.pop('memory_state')
        curr_line_no = program_state['curr_line_no']
        global_frame = program_state['global_frame']
        snapshot['curr_line_no'] = curr_line_no
        snapshot['state'] = get_html.get_state_html(global_frame, memory_state)
