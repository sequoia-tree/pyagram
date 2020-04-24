class PyagramWrappedObject:
    """
    """

    def __init__(self, state):
        self.state = state
        self.id = id(self)

    def wrap_object(self, object):
        """
        """
        self.state.memory_state.masked_objects.append(object)
        self.id = id(object)

class PyagramClassFrame(PyagramWrappedObject):
    """
    """

    HIDDEN_BINDINGS = {
        '__dict__',
        '__doc__',
        '__module__',
        '__qualname__',
        '__weakref__',
        # TODO: Are there any more that should be added add here? This should ideally include every "magic" attribute that is not a magic method -- in other words, every non-callable attribute with double-underscores on either side. Look for a complete list online.
    }

    def __init__(self, frame, *, state):
        super().__init__(state)
        state.memory_state.class_frames_by_frame[frame] = self
        self.frame = frame
        self.bindings = frame.f_locals
        self.parents = None
