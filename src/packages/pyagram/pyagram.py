import io
import sys

from . import constants
from . import encode
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
                    self.data = encode.encode_pyagram_error(exc)
                else:
                    state = pyagram_state.State(preprocessor.summary, new_stdout)
                    tracer = trace.Tracer(state)
                    bindings = {}
                    sys.stdout = new_stdout
                    try:
                        tracer.run(
                            preprocessor.ast,
                            globals=bindings,
                            locals=bindings,
                        )
                    except exception.PyagramError as exc:
                        raise exc
                    except exception.CallWrapperException as exc:
                        exempt_fn_locs.add(exc.location)
                        continue
                    except exception.UnsupportedOperatorException as exc:
                        pass # TODO
                        terminal_ex = False
                    except Exception as exc:
                        assert state.program_state.global_frame.has_returned
                        terminal_ex = True
                    else:
                        assert state.program_state.global_frame.has_returned
                        terminal_ex = False
                    postprocessor = postprocess.Postprocessor(state, terminal_ex)
                    postprocessor.postprocess()
                    self.encoding = 'result'
                    self.data = encode.encode_pyagram_result(state, postprocessor)
            except exception.PyagramError as exc:
                self.encoding = 'error'
                self.data = encode.encode_pyagram_error(exc)
            except Exception as exc:
                sys.stdout = initial_stdout
                if debug:
                    print(new_stdout.getvalue())
                    raise exc
                pyagram_error = exception.PyagramError(constants.GENERIC_ERROR_MSG)
                self.encoding = 'error'
                self.data = encode.encode_pyagram_error(pyagram_error)
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
