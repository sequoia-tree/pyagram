import io
import sys

from . import exception
from . import postprocess
from . import preprocess
from . import pyagram_state
from . import trace

class Pyagram:
    """
    """

    def __init__(self, code, *, debug):
        exempt_fn_locs = set()
        initial_stdout = sys.stdout
        while True:
            new_stdout = io.StringIO()
            try:
                try:
                    preprocessor = preprocess.Preprocessor(code, exempt_fn_locs)
                    preprocessor.preprocess()
                except SyntaxError as exc:
                    self.encoding = 'error'
                    self.data = {
                        'type': str(type(exc).__name__),
                        'lineno': exc.lineno,
                        'encoding': 'syntax',
                        'data': {
                            'code': exc.text,
                            'offset': exc.offset,
                        },
                        # TODO: Move this to encode.py.
                        # TODO: Do the same for the other assignments to self.data below.
                    }
                else:
                    bindings = {}
                    state = pyagram_state.State(preprocessor.summary, new_stdout)
                    tracer = trace.Tracer(state)
                    sys.stdout = new_stdout
                    try:
                        tracer.run(
                            preprocessor.ast,
                            globals=bindings,
                            locals=bindings,
                        )
                    except exception.CallWrapperException as exc:
                        exempt_fn_locs.add(exc.location)
                        continue
                    except exception.PyagramError as exc:
                        raise exc
                    except Exception as exc:
                        terminal_ex = True
                    else:
                        terminal_ex = False
                    assert state.program_state.global_frame.has_returned
                    postprocessor = postprocess.Postprocessor(state, terminal_ex)
                    postprocessor.postprocess()
                    self.encoding = 'result'
                    self.data = {
                        'snapshots': state.snapshots,
                        'global_data': {
                            'obj_numbers': postprocessor.obj_numbers,
                        },
                    }
            except exception.PyagramError as exc:
                self.encoding = 'error'
                self.data = {
                    'type': str(type(exc).__name__),
                    'lineno': None,
                    'encoding': 'pyagram',
                    'data': {
                        'message': exc.message,
                    },
                }
            except Exception as exc:
                sys.stdout = initial_stdout
                if debug:
                    print(new_stdout.getvalue())
                    raise exc
                exc = exception.PyagramError('message <a href="github.com">test</a>') # TODO: Pick a different variable name.
                self.encoding = 'error'
                self.data = {
                    'type': str(type(exc).__name__),
                    'lineno': None,
                    'encoding': 'pyagram',
                    'data': {
                        'message': exc.message,
                    },
                }
            else:
                sys.stdout = initial_stdout
            break

    def serialize(self):
        """
        """
        return {
            'encoding': self.encoding,
            'data': self.data,
        }
