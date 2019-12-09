import inspect # TODO: Check if this file still needs this import.

from . import encode
from . import utils

def postprocess_snapshots(snapshots):
    """
    <summary>

    :param snapshots:
    :return:
    """
    for snapshot in snapshots:
        postprocess_program_state_snapshot(snapshot['program_state'])
        postprocess_memory_state_snapshot(snapshot['memory_state'])
        postprocess_print_output_snapshot(snapshot['print_output'])

def postprocess_program_state_snapshot(program_state_snapshot):
    """
    <summary>

    :param program_state_snapshot:
    :return:
    """
    postprocess_frame_snapshot(program_state_snapshot['global_frame'])

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
    # TODO: Clean up this function a bit.

    pyagram_flag = flag_snapshot.pop('pyagram_flag')
    pyagram_frame = pyagram_flag.frame
    frame_bindings = pyagram_frame.initial_bindings # TODO: This throws an error if pyagram_frame is None, which is the case when a flag has no frame (eg for built-in calls like "a.append")
    frame_variables = list(frame_bindings)
    banner_elements = pyagram_flag.banner_elements
    banner_bindings = pyagram_flag.banner_bindings

    banner_binding_index = flag_snapshot.pop('banner_binding_index')

    # TODO: See if there's a *args param. If so, let it be param #i. Then if you encounter a numerical binding_id >= i, look not in the frame bindings but at args[binding_id - i].

    banner = []
    for banner_element in banner_elements:
        if isinstance(banner_element, str):
            banner.append([banner_element, []])
        else:
            assert isinstance(banner_element, tuple)
            code, binding_indices = banner_element
            bindings = []
            for binding_index in binding_indices:
                if binding_index < banner_binding_index:
                    binding_id = banner_bindings[binding_index]
                    is_unsupported_binding = binding_id == utils.BANNER_UNSUPPORTED_CODE
                    if is_unsupported_binding:
                        binding = encode.reference_snapshot(None, None)
                    else:
                        if isinstance(binding_id, str):

                            # TODO: Check the function's signature to see if it's actually a **kwargs.

                            binding = frame_bindings[binding_id]
                        else:
                            assert isinstance(binding_id, int)
                            if binding_id == utils.BANNER_FUNCTION_CODE:
                                binding = encode.reference_snapshot(pyagram_frame.function, pyagram_flag.state.memory_state)
                            else:

                                # TODO: Check the function's signature to see if it's actually a *args.
                                if pyagram_frame.var_positional_index is not None and pyagram_frame.var_positional_index <= binding_id:
                                    binding = pyagram_frame.initial_var_pos_args[binding_id - pyagram_frame.var_positional_index]

                                    pass # TODO: Shoot. The pyagram_frame has to take a snapshot of the initial state of its *args, if it has an *args. Then you can look at that snapshot to see what the values of the *args parameter's arguments are. (What do I mean by "take a snapshot of *args"? Basically this: args is a tuple or list or whatever. I want [reference_snapshot(elem) for elem in args].)

                                else:

                                    binding = frame_bindings[frame_variables[binding_id]]
                else:
                    binding = None
                bindings.append(binding)
            banner.append([code, bindings])
    flag_snapshot['banner'] = banner
