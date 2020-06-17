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
                        'err_data': {
                            'offset': exc.offset,
                            'code': exc.text.strip('\n'),
                        }, # TODO: Move this (and the assignments to self.data below) to encode.py.
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
                    except Exception as exc:
                        # TODO: Is there a way to stop it from raising an exception in global?
                        # TODO: Bc a problem could still occur in global, in which we should raise a PyagramError instead of concluding that everything is just fine.
                        assert state.program_state.curr_element.is_global_frame
                        terminal_ex = True
                    else:
                        terminal_ex = False
                    postprocessor = postprocess.Postprocessor(state, terminal_ex)
                    postprocessor.postprocess()
                    self.encoding = 'result'
                    self.data = {
                        'snapshots': state.snapshots,
                        'global_data': {
                            'obj_numbers': postprocessor.obj_numbers,
                        },
                    }
            except Exception as exc:
                sys.stdout = initial_stdout
                if debug:
                    print(new_stdout.getvalue())
                    raise exc
                self.encoding = 'error'
                self.data = 'TODO' # TODO
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
