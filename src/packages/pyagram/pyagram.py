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
                    } # TODO: Abstract into encode.encode_pyagram_result.
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
