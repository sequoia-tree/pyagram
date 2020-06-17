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

class PyagramException(Exception):
    """
    """

    # A PyagramException means the entire diagram (even already-encoded snapshots) may be compromised.

    pass

class HiddenSnapshotException(Exception):
    """
    """

    pass

class UnsupportedOperatorException(Exception):
    """
    """

    pass
