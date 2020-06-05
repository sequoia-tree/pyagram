from . import enum
from . import utils

class PyagramWrappedObject:
    """
    """

    def __init__(self, state):
        state.memory_state.track(self)
        self.state = state

    def wrap_object(self, object):
        """
        """
        self.state.memory_state.redirect(object, self)

class PyagramGeneratorFrame(PyagramWrappedObject):
    """
    """

    def __init__(self, generator, *, state):
        super().__init__(state)
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
    def bindings(self):
        """
        """
        return {} if self.curr_frame is None else self.curr_frame.bindings

    @property
    def results(self):
        """
        """
        if self.curr_frame is not None and self.curr_frame.shows_return_value:
            return self.curr_frame.return_value, self.curr_frame.yield_from
        if self.prev_frame is not None and self.prev_frame.shows_return_value:
            return self.prev_frame.return_value, self.prev_frame.yield_from
        return None

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
        state.memory_state.pg_class_frames[frame] = self
        self.frame = frame
        self.class_obj = None
        self.initial_bases = None

    @property
    def bindings(self):
        """
        """
        bindings = self.frame.f_locals if self.class_obj is None else self.class_obj.__dict__
        return {
            variable: value
            for variable, value in bindings.items()
            if variable not in PyagramClassFrame.HIDDEN_BINDINGS
        }
