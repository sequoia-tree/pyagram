from . import enum

class PyagramWrappedObject:
    """
    """

    def __init__(self, state, *, object_type=None):
        if object_type is None:
            state.memory_state.track(self)
        else:
            state.memory_state.track(self, object_type)
        self.state = state

    def wrap_object(self, object):
        """
        """
        self.state.memory_state.wrapped_obj_ids[id(object)] = id(self)

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
        super().__init__(state, object_type=enum.ObjectTypes.OBJ_CLASS)
        state.memory_state.pg_class_frames[frame] = self
        self.frame = frame
        self.bindings = frame.f_locals
        self.parents = None

class PyagramGenerator(PyagramWrappedObject):
    """
    """

    def __init__(self, generator, function, *, state):
        super().__init__(state, object_type=enum.ObjectTypes.GENERATOR)
        self.wrap_object(generator)
        self.generator = generator
        self.function = function
        self.has_returned = False
        self.return_value = None

    def close(self, return_value):
        """
        """
        self.has_returned = True
        self.return_value = return_value
