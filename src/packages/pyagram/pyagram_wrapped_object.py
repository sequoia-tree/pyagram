class PyagramWrappedObject:
    """
    """

    pass

# TODO: Make it so any subclass of PyagramWrappedObject can have that behavior where you use some wrapped object's ID as its own.

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
        self.id = id(self)
        self.state = state
        self.frame = frame
        self.parents = None
        self.bindings = frame.f_locals
        self.state.memory_state.class_frames_by_frame[frame] = self
