import trace

class Pyagram:
    """
    <summary>
    """

    def __init__(self, code):
        tracer = trace.Tracer(self)
        tracer.run(code, {}, {})

    # Basically a Pyagram object is a list of InstantaneousState objects.
