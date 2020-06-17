class PyagramError(Exception):
    """
    """

    # A PyagramError means the entire diagram (even already-encoded snapshots) may be compromised.

    def __init__(self, message):
        self.message = message

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

class UnsupportedOperatorException(Exception):
    """
    """

    def __init__(self, fn_name):
        self.fn_name = fn_name

    @property
    def message(self):
        """
        """
        return f'Pyagram does not support the interactive function `{self.fn_name}`'
