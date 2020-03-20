import ast
import astunparse

OPEN_PARENTHESIS, CLOSE_PARENTHESIS = ast.Str('('), ast.Str(')')
OPEN_STARRED_LIST, CLOSE_STARRED_LIST = ast.Str('*['), ast.Str(']')
OPEN_STARRED_TUPLE, CLOSE_STARRED_TUPLE = ast.Str('*('), ast.Str(')')
OPEN_KEYWORD_DICT, CLOSE_KEYWORD_DICT = ast.Str('**{'), ast.Str('}')
COMMA = ast.Str(', ')

class Banner:
    """
    <summary>

    :param node:
    """

    def __init__(self, node):
        self.elements = []
        self.bindings = []
        self.has_prev_input = False
        self.add_func_info(node.func)
        self.elements.append(OPEN_PARENTHESIS)
        self.add_args_info(node.args)
        self.add_kwds_info(node.keywords)
        self.elements.append(CLOSE_PARENTHESIS)

    @property
    def banner(self):
        """
        <summary>

        :return:
        """
        return ast.Tuple(
            elts=[
                ast.List(elts=self.elements, ctx=ast.Load()),
                ast.List(elts=self.bindings, ctx=ast.Load()),
            ],
            ctx=ast.Load(),
        )

    def add_func_info(self, func):
        """
        <summary>

        :param func:
        :return:
        """
        self.add_bindings(func)

    def add_args_info(self, args):
        """
        <summary>

        :param args:
        :return:
        """
        for arg in args:
            if self.has_prev_input:
                self.elements.append(COMMA)
            if isinstance(arg, ast.Starred):
                if isinstance(arg.value, ast.List):
                    self.elements.append(OPEN_STARRED_LIST)
                    self.has_prev_input = False
                    self.add_args_info(arg.value.elts)
                    self.elements.append(CLOSE_STARRED_LIST)
                elif isinstance(arg.value, ast.Tuple):
                    self.elements.append(OPEN_STARRED_TUPLE)
                    self.has_prev_input = False
                    self.add_args_info(arg.value.elts)
                    self.elements.append(CLOSE_STARRED_TUPLE)
                elif isinstance(arg.value, ast.Str):
                    values = (*arg.value.s,)
                    params = (None,) * len(values)
                    self.add_bindings(arg, values, params)
                else:
                    self.add_bindings(arg, (), ())
            else:
                self.add_bindings(arg)
            self.has_prev_input = True

    def add_kwds_info(self, kwds):
        """
        <summary>

        :param kwds:
        :return:
        """
        kwds = list(zip(kwds.keys, kwds.values)) if isinstance(kwds, ast.Dict) else [(None if kwd.arg is None else ast.Str(kwd.arg), kwd.value) for kwd in kwds]
        for param, arg in kwds:
            if self.has_prev_input:
                self.elements.append(COMMA)
            if param is None:
                if isinstance(arg, ast.Dict):
                    self.elements.append(OPEN_KEYWORD_DICT)
                    self.has_prev_input = False
                    self.add_kwds_info(arg)
                    self.elements.append(CLOSE_KEYWORD_DICT)
                else:
                    self.add_bindings(arg, (), ())
            else:
                self.elements.append(ast.Str(f'{param.s}='))
                self.add_bindings(arg, (arg,), (param,))
            self.has_prev_input = True

    def add_bindings(self, node, values=None, params=None):
        """
        <summary>

        :param node:
        :param values:
        :param params:
        :return:
        """
        is_unsupported_binding = values == () and params == ()
        if values is None and params is None:
            values = (node,)
            params = (None,)
        assert len(values) == len(params)
        code = ast.Str(astunparse.unparse(node).strip('\n')) # TODO: You may be able to circumvent the necessity for astunparse if you can leverage <node>.col_offset and <node>.end_col_offset.
        bindings = []
        if is_unsupported_binding:
            binding = ast.NameConstant(None) # TODO: When binding_info is None, the binding is unsupported -- ie it's a `*args` or `**kwargs` expression where `args` is not a list, tuple, or string / `kwargs` is not a dict. In such cases render the binding as a question mark. If you click on the question mark, you should be brought to the Pyagram GitHub Issues page, where there should be an issue describing the fact that this behaviour is not currently supported.
            bindings.append(binding)
        else:
            for value, param in zip(values, params):
                is_call = ast.NameConstant(isinstance(value, ast.Call))
                param_if_known = ast.NameConstant(None) if param is None else param
                binding = ast.Tuple(elts=[is_call, param_if_known], ctx=ast.Load())
                bindings.append(binding)
        binding_indices = []
        for binding in bindings:
            binding_indices.append(ast.Num(len(self.bindings)))
            self.bindings.append(binding)
        banner_element = ast.Tuple(
            elts=[code, ast.List(elts=binding_indices, ctx=ast.Load())],
            ctx=ast.Load(),
        )
        self.elements.append(banner_element)
