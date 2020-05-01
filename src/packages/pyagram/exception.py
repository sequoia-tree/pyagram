class HiddenSnapshotException(Exception):
    """
    """

    pass

class UserException(Exception): # TODO: Currently unused, I think.
    """
    """

    def __init__(self, exception_type, exception_value, traceback):
        super().__init__(self)
        self.type = exception_type
        self.value = exception_value
        self.traceback = traceback
