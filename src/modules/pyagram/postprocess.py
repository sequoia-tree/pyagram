from . import encode
from . import utils

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
    pyagram_flag = flag_snapshot.pop('pyagram-flag')
    banner_elements, banner_bindings = flag_snapshot['banner']
    pyagram_frame = pyagram_flag.frame
    frame_bindings = pyagram_frame.initial_bindings # TODO: This throws an error if pyagram_frame is None, which is the case when a flag has no frame (eg for built-in calls like "a.append")
    frame_variables = list(frame_bindings)

    banner = []
    for banner_element in banner_elements:
        if isinstance(banner_element, str):
            banner.append(banner_element)
        else:
            assert isinstance(banner_element, tuple)
            code, binding_indices = banner_element
            bindings = []
            for binding_index in binding_indices:
                binding_id = banner_bindings[binding_index]
                is_unsupported_binding = binding_id == utils.BANNER_UNSUPPORTED_CODE
                if is_unsupported_binding:
                    binding_reference_snapshot = encode.reference_snapshot(None, None)
                else:
                    if isinstance(binding_id, str):
                        binding = frame_bindings[binding_id]
                    elif isinstance(binding_id, int):
                        if binding_id == utils.BANNER_FUNCTION_CODE:
                            binding = pyagram_frame.function
                        else:
                            binding = frame_bindings[frame_variables[binding_id]]
                    else:
                        binding = None
                    binding_reference_snapshot = encode.reference_snapshot(binding, pyagram_flag.state.memory_state)
                bindings.append(binding_reference_snapshot)
            banner.append([code, bindings])
    flag_snapshot['banner'] = banner
