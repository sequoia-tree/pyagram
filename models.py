class InstantaneousState:
    """
    <summary>
    """

    def __init__(self):
        pass

    # Represents the state of the program at a particular step in time.
    # Contain a pointer to a PyagramFrame representing the global frame at a particular time.
    # Maintains a print output.

class PyagramFrame:
    """
    <summary>
    """

    def __init__(self, locals):
        self.locals = locals
        self.return_value = None
        self.has_returned = False

class PyagramFlag:
    """
    <summary>
    """

    def __init__(self):
        pass
