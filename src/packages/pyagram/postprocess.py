from . import encode
from . import utils

class Postprocessor:
    """
    """

    def __init__(self, state):
        self.state = state

    def postprocess(self):
        self.hide_hidden_snapshots()
        self.postprocess_snapshots()
        self.kill_hidden_snapshots()
        self.kill_static_snapshots()

    def postprocess_snapshots(self):
        for snapshot in self.state.snapshots:
            if snapshot is not None:
                self.postprocess_frame_snapshot(snapshot['program_state']['global_frame'])

    def postprocess_element_snapshot(self, element_snapshot):
        """
        """
        for flag_snapshot in element_snapshot['flags']:
            self.postprocess_flag_snapshot(flag_snapshot)

    def postprocess_flag_snapshot(self, flag_snapshot):
        """
        <summary>

        :param flag_snapshot:
        :return:
        """
        self.interpolate_flag_banner(flag_snapshot)
        frame_snapshot = flag_snapshot['frame']
        if frame_snapshot is not None:
            self.postprocess_frame_snapshot(frame_snapshot)
        self.postprocess_element_snapshot(flag_snapshot)

    def postprocess_frame_snapshot(self, frame_snapshot):
        """
        <summary>

        :frame_snapshot:
        :return:
        """
        self.postprocess_element_snapshot(frame_snapshot)

    def hide_hidden_snapshots(self):
        for hidden_flag in self.state.hidden_flags:
            start_index = hidden_flag.start_index
            close_index = hidden_flag.close_index
            for i in range(start_index, close_index + 1):
                self.state.snapshots[i] = None

    def kill_hidden_snapshots(self):
        i = 0
        while i < len(self.state.snapshots):
            if self.state.snapshots[i] is None:
                del self.state.snapshots[i]
            else:
                i += 1

    def kill_static_snapshots(self):
        i = len(self.state.snapshots) - 1
        while 0 < i:
            former_snapshot = self.state.snapshots[i - 1]
            latter_snapshot = self.state.snapshots[i]
            # TODO: We temporarily remove the lineno because that's the only part of the snapshot we don't want to compare. If you never end up using the lineno at all in the visualization, then you shouldn't even include it from the program_state snapshot.
            former_line_no = former_snapshot['program_state'].pop('curr_line_no')
            latter_line_no = latter_snapshot['program_state'].pop('curr_line_no')
            if former_snapshot == latter_snapshot:
                del self.state.snapshots[i]
            former_snapshot['program_state']['curr_line_no'] = former_line_no
            latter_snapshot['program_state']['curr_line_no'] = latter_line_no
            i -= 1

    def interpolate_flag_banner(self, flag_snapshot):
        """
        <summary>

        :flag_snapshot:
        :return:
        """
        # TODO: Clean up this function a bit.

        pyagram_flag = flag_snapshot.pop('pyagram_flag')
        pyagram_frame = pyagram_flag.frame

        has_frame = pyagram_frame is not None
        if has_frame:
            frame_bindings = pyagram_frame.initial_bindings
            frame_variables = list(frame_bindings)
        else:
            assert self.state.program_state.exception_snapshot is not None

        banner_elements = pyagram_flag.banner_elements
        banner_bindings = pyagram_flag.banner_bindings

        banner_binding_index = flag_snapshot.pop('banner_binding_index')

        snapshot_index = flag_snapshot.pop('snapshot_index')

        banner = []
        for banner_element in banner_elements:
            if isinstance(banner_element, str):
                banner.append([banner_element, []])
            else:
                assert isinstance(banner_element, tuple)
                code, binding_indices = banner_element
                if has_frame:
                    bindings = []
                    for binding_index in binding_indices:
                        if binding_index < banner_binding_index:
                            binding_id = banner_bindings[binding_index]
                            is_unsupported_binding = binding_id == utils.BANNER_UNSUPPORTED_CODE
                            if is_unsupported_binding:
                                binding = self.state.encoder.reference_snapshot(None, None) # TODO: Add an issues to the Github Issues page for this too.
                            else:
                                if isinstance(binding_id, str):

                                    # See if there's a **kwargs param. If so, let it be param #i. Then if you encounter a keyword binding, look first in the frame and then in the **kwargs dictionary.
                                    if binding_id in frame_bindings:
                                        binding = frame_bindings[binding_id]
                                    else:
                                        assert pyagram_frame.initial_var_keyword_args is not None
                                        binding = pyagram_frame.initial_var_keyword_args[binding_id]

                                else:
                                    assert isinstance(binding_id, int)
                                    if binding_id == utils.BANNER_FUNCTION_CODE:
                                        binding = self.state.encoder.reference_snapshot(pyagram_frame.function, pyagram_flag.state.memory_state)
                                    else:

                                        # See if there's a *args param. If so, let it be param #i. Then if you encounter a numerical binding_id >= i, look not in the frame bindings but at args[binding_id - i].

                                        if pyagram_frame.var_positional_index is not None and pyagram_frame.var_positional_index <= binding_id:
                                            binding = pyagram_frame.initial_var_pos_args[binding_id - pyagram_frame.var_positional_index]
                                        else:

                                            binding = frame_bindings[frame_variables[binding_id]]
                        else:
                            binding = None # This means the box is drawn empty. We haven't gotten around to evaluating that binding yet.
                        bindings.append(binding)
                        if type(binding) is int: # This means the binding refers to an object in memory.
                            self.enforce_early_debut(binding, snapshot_index)
                else:
                    bindings = [self.state.encoder.reference_snapshot(None, None)]
                banner.append([code, bindings])
        flag_snapshot['banner'] = banner

    def enforce_early_debut(self, object_id, new_debut_index):
        """
        """

        # The flag snapshot should include the index i of the snapshot. If you come across a binding that's an object (i.e. a binding of type int), which first appears in the jth snapshot's memory state where j > i, then go back and insert it into the memory states of snapshots i ... j-1. (You should copy over the version of the object from snapshot j, rather than the last snapshot, because it may later be mutated.) Moreover, suppose you do this, and in so doing you insert the object into the kth index of snapshot i's memory state; then you should also move it up to the kth index of snapshots j, j+1, .... (The order matters so that objects stay in the same order when a student passes in keyword arguments in a different order than they appear in a function's signature.)

        debut_index = self.state.memory_state.object_debuts[object_id]
        debut_snapshot = None

        debut_memory_state = self.state.snapshots[debut_index]['memory_state']
        new_debut_memory_state = self.state.snapshots[new_debut_index]['memory_state']

        if new_debut_index < debut_index:

            memory_state_index = None
            for i in range(len(debut_memory_state)):
                object_snapshot = debut_memory_state[i]
                if object_id == object_snapshot['id']:
                    assert debut_snapshot is None and memory_state_index is None
                    debut_snapshot = object_snapshot['object']
                    memory_state_index = i
            assert debut_snapshot is not None and memory_state_index is not None
            new_memory_state_index = len(new_debut_memory_state)

            for snapshot_index in range(new_debut_index, debut_index):
                snapshot = self.state.snapshots[snapshot_index]
                if snapshot is not None:
                    snapshot['memory_state'].insert(
                        new_memory_state_index,
                        {
                            'id': object_id,
                            'object': debut_snapshot,
                        },
                    )

            for snapshot_index in range(debut_index, len(self.state.snapshots)):
                snapshot = self.state.snapshots[snapshot_index]
                if snapshot is not None:
                    object_snapshot = snapshot['memory_state'].pop(memory_state_index)
                    snapshot['memory_state'].insert(new_memory_state_index, object_snapshot)

            self.state.memory_state.object_debuts[object_id] = new_debut_index
