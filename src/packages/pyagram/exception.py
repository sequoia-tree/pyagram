class CallWrapperException(Exception):
    """
    """

    def __init__(self, lineno, col_offset):
        self.lineno = lineno
        self.col_offset = col_offset

    @property
    def location(self):
        """
        """
        return (self.lineno, self.col_offset)

class HiddenSnapshotException(Exception):
    """
    """

    pass
