import json

import pyagram

class PyagramEncoder(json.JSONEncoder):
    """
    <summary>
    """

    def default(self, object):
        """
        <summary>

        :param object:
        :return:
        """
        if isinstance(object, pyagram.Pyagram):
            return {} # TODO
        else:
            return super().default(object)
