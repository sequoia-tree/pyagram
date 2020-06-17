from . import constants
from . import encode
from . import enum
from . import exception
from . import utils

class Postprocessor:
    """
    """

    def __init__(self, state, terminal_ex):
        self.state = state
        self.terminal_ex = terminal_ex
        self.obj_numbers = {}

    def postprocess(self):
        """
        """
        self.kill_excess_snapshots()
        self.postprocess_snapshots()
        self.kill_hidden_snapshots()
        self.kill_static_snapshots() # TODO: Consider deleting this.
        self.encode_object_numbers()

    def kill_excess_snapshots(self):
        """
        """
        if self.terminal_ex:
            while self.state.snapshots[-1]['exception'] is None: # TODO: Do you still need this?
                # TODO: Instead of deleting snapshots in reverse order from the end, maybe you can leverage the state.program_state.exception_index?
                self.state.snapshots.pop()

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

        if pyagram_flag in self.state.program_state.new_banners:
            # TODO: Kinda messy, maybe at least abstract it.
            old_fn_code = flag_snapshot['banner'][0]['code']
            new_fn_code = self.state.program_state.new_banners[pyagram_flag]
            if old_fn_code == new_fn_code:
                del self.state.program_state.new_banners[pyagram_flag]
            else:
                flag_snapshot['banner'][0]['code'] = new_fn_code

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
        for encode_object in memory_snapshot:
            encoding = encode_object['object']['encoding']
            snapshot = encode_object['object']['data']
            if encoding == 'class' and 'self' in snapshot:
                class_frame = snapshot.pop('self')
                if snapshot['parents'] is None:
                    snapshot['parents'] = class_frame.initial_bases

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
        for i, encode_object in enumerate(self.state.snapshots[-1]['memory_state']):
            self.obj_numbers[encode_object['id']] = i + 1
