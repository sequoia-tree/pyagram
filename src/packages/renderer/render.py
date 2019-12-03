from . import get_html

def render_components(snapshots):
    """
    <description>

    :param snapshots:
    :return:
    """
    for snapshot in snapshots:
        render_program_state(snapshot['program_state'])
        render_memory_state(snapshot['memory_state'])
        render_print_output(snapshot['print_output'])

def render_program_state(program_state_snapshot):
    """
    <description>

    :param program_state_snapshot:
    :return:
    """
    program_state_snapshot['global_frame'] = get_html.get_frame_html(program_state_snapshot['global_frame'])

def render_memory_state(memory_state_snapshot):
    """
    <description>

    :param memory_state_snapshot:
    :return:
    """
    pass # TODO

def render_print_output(print_output_snapshot):
    """
    <description> # Give docstrings to the rest of the functions in this file and in get_html.py

    :param print_output_snapshot:
    :return:
    """
    pass
