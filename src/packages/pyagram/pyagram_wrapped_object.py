from . import enum
from . import utils

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

class PyagramGeneratorFrame(PyagramWrappedObject):
    """
    """

    def __init__(self, generator, *, state):
        super().__init__(state, object_type=enum.ObjectTypes.GENERATOR)
        state.memory_state.pg_generator_frames[generator] = self
        self.generator = generator
        self.wrap_object(generator)
        generator_function = utils.get_function(generator.gi_frame)
        if generator_function is None:
            parent = state.program_state.curr_element
        else:
            parent = state.memory_state.function_parents[generator_function]
        self.number = self.state.program_state.register_frame()
        self.parent = parent
        self.prev_frame = None
        self.curr_frame = None

    @property
    def return_frame(self):
        """
        """
        return self.curr_frame if self.curr_frame.shows_return_value else self.prev_frame

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
        super().__init__(state, object_type=enum.ObjectTypes.USER_CLASS)
        state.memory_state.pg_class_frames[frame] = self
        self.frame = frame
        self.bindings = frame.f_locals
        self.parents = None
