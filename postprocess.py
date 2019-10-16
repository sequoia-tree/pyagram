def postprocess_snapshots(snapshots):
    """
    <summary>

    :param snapshots:
    :return:
    """
    for snapshot in snapshots:
        postprocess_program_state_snapshot(snapshot['program-state'])
        postprocess_memory_state_snapshot(snapshot['memory-state'])
        postprocess_print_output_snapshot(snapshot['print-output'])

def postprocess_program_state_snapshot(program_state_snapshot):
    """
    <summary>

    :param program_state_snapshot:
    :return:
    """
    postprocess_frame_snapshot(program_state_snapshot['global-frame'])

def postprocess_memory_state_snapshot(memory_state_snapshot):
    """
    <summary>

    :param memory_state_snapshot:
    :return:
    """
    pass

def postprocess_print_output_snapshot(print_output_snapshot):
    """
    <summary>

    :param print_output_snapshot:
    :return:
    """
    pass

def postprocess_element_snapshot(element_snapshot):
    """
    <summary>

    :param element_snapshot:
    :return:
    """
    for flag_snapshot in element_snapshot['flags']:
        postprocess_flag_snapshot(flag_snapshot)

def postprocess_flag_snapshot(flag_snapshot):
    """
    <summary>

    :param flag_snapshot:
    :return:
    """
    interpolate_flag_banner(flag_snapshot)
    frame_snapshot = flag_snapshot['frame']
    if frame_snapshot is not None:
        postprocess_frame_snapshot(frame_snapshot)
    postprocess_element_snapshot(flag_snapshot)

def postprocess_frame_snapshot(frame_snapshot):
    """
    <summary>

    :frame_snapshot:
    :return:
    """
    postprocess_element_snapshot(frame_snapshot)

def interpolate_flag_banner(flag_snapshot):
    """
    <summary>

    :flag_snapshot:
    :return:
    """
    # TODO: Maybe move this directly into postprocess_flag_snapshot?
    pass
    # pyagram_flag = flag_snapshot.pop('pyagram-flag')

    # pass # TODO: Finish PyagramFlag first!

    # flag_snapshot['banner'] = None # TODO

    # # TODO: At the end of this function, flag_snapshot['flag-info'] should be a mix of strings and BINDINGS, eg
    # # [BINDING, '(', BINDING, ', ', BINDING, ')'] where
    # # BINDING = [code string, [X, X, X, ...]] where
    # # each X = None, if this binding should not yet appear in the flag
    # #        = integer (a memory id), if this binding is a pointer
    # #        = string (of whatever the binding is for), if this binding is a primitive
    # # TODO: Use reference_snapshot(...) to produce each X.
