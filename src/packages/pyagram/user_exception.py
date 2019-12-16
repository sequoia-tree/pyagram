class UserException(Exception):
    """
    """

    def __init__(self, exception_type, exception_value, traceback):
        super().__init__(self)
        self.type = exception_type
        self.value = exception_value
        self.traceback = traceback
