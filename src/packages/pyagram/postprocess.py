from . import constants
from . import encode
from . import enum
from . import exception
from . import utils

class Postprocessor:
    """
    """

    def __init__(self, state):
        self.state = state
        self.obj_numbers = {}

    def postprocess(self):
        """
        """
        self.postprocess_snapshots()
        self.kill_hidden_snapshots()
        self.kill_static_snapshots() # TODO: Consider deleting this.
        self.encode_object_numbers() # TODO: Employ this map in in decode.js and templates.js for the text-based pointer representation visualization option later on.

    def postprocess_snapshots(self):
        """
        """
        for i, snapshot in enumerate(self.state.snapshots):
            try:
                self.postprocess_frame_snapshot(i, snapshot['global_frame'])
                self.postprocess_memory_snapshot(i, snapshot['memory_state'])
            except exception.HiddenSnapshotException:
                self.state.snapshots[i] = None

    def postprocess_element_snapshot(self, snapshot_index, element_snapshot):
        """
        """
        i, flags = 0, element_snapshot['flags']
        while i < len(flags):
            if self.postprocess_flag_snapshot(snapshot_index, flags[i]) == constants.HIDDEN_FLAG_CODE:
                flags[i : i + 1] = flags[i]['flags']
            else:
                i += 1

    def postprocess_flag_snapshot(self, snapshot_index, flag_snapshot):
        """
        """
        pyagram_flag = flag_snapshot.pop('self')
        if pyagram_flag.is_hidden(snapshot_index):
            if flag_snapshot['is_curr_element']:
                raise exception.HiddenSnapshotException()
            else:
                return constants.HIDDEN_FLAG_CODE
        self.interpolate_flag_banner(flag_snapshot, pyagram_flag)
        frame_snapshot = flag_snapshot['frame']
        if frame_snapshot is not None:
            self.postprocess_frame_snapshot(snapshot_index, frame_snapshot)
        self.postprocess_element_snapshot(snapshot_index, flag_snapshot)

    def postprocess_frame_snapshot(self, snapshot_index, frame_snapshot):
        """
        """
        self.postprocess_element_snapshot(snapshot_index, frame_snapshot)

    def postprocess_memory_snapshot(self, snapshot_index, memory_snapshot):
        """
        """
        for object_snapshot in memory_snapshot:
            encoding = object_snapshot['object']['encoding']
            snapshot = object_snapshot['object']['data']
            if encoding == 'obj_class':
                class_frame = snapshot.pop('self')
                snapshot['parents'] = None if class_frame.parents is None else [parent.__name__ for parent in class_frame.parents]

    def kill_hidden_snapshots(self):
        """
        """
        i = 0
        while i < len(self.state.snapshots):
            if self.state.snapshots[i] is None:
                del self.state.snapshots[i]
            else:
                i += 1

    def kill_static_snapshots(self):
        """
        """
        # TODO: After you finish implementing the snapshotting logic in pyagram_state.py, see if you still need this function.
        # TODO: If you keep this function, make it count up from 0, not down from len.
        # TODO: Refactor / clean up this function.
        i = len(self.state.snapshots) - 1
        while 0 < i:
            former_snapshot = self.state.snapshots[i - 1]
            latter_snapshot = self.state.snapshots[i]
            former_line_no = former_snapshot.pop('curr_line_no')
            latter_line_no = latter_snapshot.pop('curr_line_no')
            if former_snapshot == latter_snapshot:
                del self.state.snapshots[i]
            former_snapshot['curr_line_no'] = former_line_no
            latter_snapshot['curr_line_no'] = latter_line_no
            i -= 1

    def encode_object_numbers(self):
        """
        """
        for i, object_snapshot in enumerate(self.state.snapshots[-1]['memory_state']):
            self.obj_numbers[object_snapshot['id']] = i + 1

    def interpolate_flag_banner(self, flag_snapshot, pyagram_flag):
        """
        """
        pyagram_frame = pyagram_flag.frame
        has_frame = pyagram_frame is not None
        if has_frame:
            frame_bindings = pyagram_frame.initial_bindings
            frame_variables = list(frame_bindings)
        else:
            pass # TODO: The bindings should all be enum.ObjectTypes.UNKNOWN.
        banner_elements = pyagram_flag.banner_elements
        banner_bindings = pyagram_flag.banner_bindings
        banner_binding_index = flag_snapshot.pop('banner_binding_index')
        snapshot_index = flag_snapshot.pop('snapshot_index')
        banner = []
        for banner_element in banner_elements:
            if isinstance(banner_element, str):
                banner.append({
                    'code': banner_element,
                    'bindings': [],
                })
            else:
                assert isinstance(banner_element, tuple)
                code, binding_indices = banner_element
                if has_frame:
                    bindings = []
                    for binding_index in binding_indices:
                        if binding_index < banner_binding_index:
                            binding_id = banner_bindings[binding_index]
                            is_unsupported_binding = binding_id == constants.BANNER_UNSUPPORTED_CODE
                            if is_unsupported_binding:
                                binding = self.state.encoder.reference_snapshot(enum.ObjectTypes.UNKNOWN)
                            else:
                                if isinstance(binding_id, str):

                                    # See if there's a **kwargs param. If so, let it be param #i. Then if you encounter a keyword binding, look first in the **kwargs dictionary and then in the frame.

                                    if pyagram_frame.initial_var_keyword_args is not None and binding_id in pyagram_frame.initial_var_keyword_args:
                                        binding = pyagram_frame.initial_var_keyword_args[binding_id]
                                    else:
                                        binding = frame_bindings[binding_id]
                                else:
                                    assert isinstance(binding_id, int)
                                    if binding_id == constants.BANNER_FUNCTION_CODE:
                                        binding = self.state.encoder.reference_snapshot(pyagram_frame.function)
                                    else:

                                        # See if there's a *args param. If so, let it be param #i. Then if you encounter a numerical binding_id >= i, look not in the frame bindings but at args[binding_id - i].

                                        if pyagram_frame.var_positional_index is not None and pyagram_frame.var_positional_index <= binding_id:
                                            binding = pyagram_frame.initial_var_pos_args[binding_id - pyagram_frame.var_positional_index]
                                        else:
                                            binding = frame_bindings[frame_variables[binding_id]]
                        else:

                            # This means the box is drawn empty. We haven't gotten around to evaluating that binding yet.

                            binding = None
                        bindings.append(binding)
                        if type(binding) is int:

                            # This means the binding refers to an object in memory.

                            self.enforce_early_debut(binding, snapshot_index)
                else:
                    bindings = [self.state.encoder.reference_snapshot(enum.ObjectTypes.UNKNOWN)]
                banner.append({
                    'code': code,
                    'bindings': bindings,
                })
        flag_snapshot['banner'] = banner

    def enforce_early_debut(self, object_id, new_debut_index):
        """
        """

        # The flag snapshot should include the index i of the snapshot. If you come across a binding that's an object (i.e. a binding of type int), which first appears in the jth snapshot's memory state where j > i, then go back and insert it into the memory states of snapshots i ... j-1. (You should copy over the version of the object from snapshot j, rather than the last snapshot, because it may later be mutated.) Moreover, suppose you do this, and in so doing you insert the object into the kth index of snapshot i's memory state; then you should also move it up to the kth index of snapshots j, j+1, .... (The order matters so that objects stay in the same order when a student passes in keyword arguments in a different order than they appear in a function's signature.)

        debut_index, debut_snapshot = self.state.memory_state.obj_init_debuts[object_id], None
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
            self.state.memory_state.obj_init_debuts[object_id] = new_debut_index
