import ast
import astunparse

INNER_CALL_LINENO = -1
OUTER_CALL_LINENO = -2

OPEN_PARENTHESIS = ast.Str('(')
CLOSE_PARENTHESIS = ast.Str(')')
COMMA = ast.Str(', ')
OPEN_STARRED_LIST = ast.Str('*[')
CLOSE_STARRED_LIST = ast.Str(']')
OPEN_STARRED_TUPLE = ast.Str('*(')
CLOSE_STARRED_TUPLE = ast.Str(')')
OPEN_KEYWORD_DICT = ast.Str('**{')
CLOSE_KEYWORD_DICT = ast.Str('}')

class CallWrapper(ast.NodeTransformer):
    """
    <summary>
    """

    def __init__(self):
        super().__init__()
        self.id_counter = 0

    def visit_Call(self, node):
        """
        <summary>

        :param node: An ast.Call node representing some function call `f(x)`.
        :return: An ast.Call node representing `nop(nop(flag_info, id), f(x), id)`
            where `flag_info` is the information required by the flag banner, and
            `id` uniquely identifies the flag.
        """

        # Or I guess more accurately ...
        # f(...) --> (lambda banner, call: call)(
        #                (lambda: flag_info)(),
        #                f(...),
        #            )

        # TODO: Are there nodes other than Call nodes (eg listcomp, dictcomp, etc) that create their own frames? If so, we need to mutate those too. And also flag_info bitmap should account for them too (not just Call nodes).

        inner_lambda = ast.Lambda(
            args=ast.arguments(
                args=[],
                vararg=None,
                kwonlyargs=[],
                kwarg=None,
                defaults=[],
                kw_defaults=[],
            ),
            body=get_flag_info(node),
        )
        outer_lambda = ast.Lambda(
            args=ast.arguments(
                args=[
                    ast.arg(arg='banner', annotation=None),
                    ast.arg(arg='call', annotation=None),
                ],
                vararg=None,
                kwonlyargs=[],
                kwarg=None,
                defaults=[],
                kw_defaults=[],
            ),
            body=ast.Name(id='call', ctx=ast.Load()),
        )
        inner_call = ast.Call(
            func=inner_lambda,
            args=[],
            keywords=[],
            lineno=INNER_CALL_LINENO,
            col_offset=self.id_counter,
        )
        outer_call = ast.Call(
            func=outer_lambda,
            args=[
                inner_call,
                node,
            ],
            keywords=[],
            lineno=OUTER_CALL_LINENO,
            col_offset=self.id_counter,
        )
        self.id_counter += 1 # An outer_call and inner_call correspond to one another iff they have the same ID. (But at the moment we don't actually use that information; we just have it there bc it's nice.)
        self.generic_visit(node)
        return outer_call

def get_flag_info(node):
    """
    <summary>
    
    :node:
    :return:
    """
    flag_info = []
    add_func_info(flag_info, node.func)
    flag_info.append(OPEN_PARENTHESIS)
    has_prev_input = False
    has_prev_input = add_args_info(flag_info, has_prev_input, node.args)
    has_prev_input = add_kwds_info(flag_info, has_prev_input, node.keywords)
    flag_info.append(CLOSE_PARENTHESIS)
    return ast.List(elts=flag_info, ctx=ast.Load())

def add_func_info(flag_info, func):
    """
    <summary>

    :flag_info:
    :func:
    :return:
    """
    add_banner_binding(flag_info, func)

def add_args_info(flag_info, has_prev_input, args):
    """
    <summary>

    :flag_info:
    :has_prev_input:
    :args:
    :return:
    """
    for arg in args:
        if has_prev_input:
            flag_info.append(COMMA)
        if isinstance(arg, ast.Starred):
            if isinstance(arg.value, ast.List):
                flag_info.append(OPEN_STARRED_LIST)
                add_args_info(flag_info, has_prev_input, arg.value.elts)
                flag_info.append(CLOSE_STARRED_LIST)
            elif isinstance(arg.value, ast.Tuple):
                flag_info.append(OPEN_STARRED_TUPLE)
                add_args_info(flag_info, has_prev_input, arg.value.elts)
                flag_info.append(CLOSE_STARRED_TUPLE)
            elif isinstance(arg.value, ast.Str):
                values = (*arg.value.s,)
                params = (None,) * len(values)
                add_banner_binding(flag_info, arg, values, params)
            else:
                add_banner_binding(flag_info, arg, (), ())
        else:
            add_banner_binding(flag_info, arg)
        has_prev_input = True
    return has_prev_input

def add_kwds_info(flag_info, has_prev_input, kwds):
    """
    <summary>

    :flag_info:
    :has_prev_input:
    :kwds:
    :return:
    """
    kwds = list(zip(kwds.keys, kwds.values)) if isinstance(kwds, ast.Dict) else [(kwd.arg, kwd.value) for kwd in kwds]
    for param, arg in kwds:
        if has_prev_input:
            flag_info.append(COMMA)
        if param is None:
            if isinstance(arg, ast.Dict):
                flag_info.append(OPEN_KEYWORD_DICT)
                add_kwds_info(flag_info, has_prev_input, arg)
                flag_info.append(CLOSE_KEYWORD_DICT)
            else:
                add_banner_binding(flag_info, arg, (), ())
        else:
            flag_info.append(ast.Str(f'{param}='))
            add_banner_binding(flag_info, arg, (arg,), (param,))
        has_prev_input = True
    return has_prev_input

def add_banner_binding(flag_info, node, values=None, params=None):
    """
    <summary>

    :flag_info:
    :node:
    :values:
    :params:
    :return:
    """
    is_unsupported_binding = values == () and params == ()
    if values is None and params is None:
        values = (node,)
        params = (None,)
    assert len(values) == len(params)
    binding_expr = ast.Str(astunparse.unparse(node))
    binding_info = ast.NameConstant(None) if is_unsupported_binding else ast.List(elts=[ # TODO: When binding_info is None, the binding is unsupported -- it it's a `*args` or `**kwargs` expression where `args` is not a list, tuple, or string / `kwargs` is not a dict. In such cases render the binding as a question mark. If you click on the question mark, you should be brought to the Pyagram GitHub Issues page, where there should be an issue describing the fact that this behaviour is not currently supported.
        ast.Tuple(elts=[
            ast.NameConstant(isinstance(value, ast.Call)),
            ast.NameConstant(None) if param is None else ast.Str(param),
        ], ctx=ast.Load())
        for value, param in zip(values, params)
    ], ctx=ast.Load())
    flag_info.append(ast.Tuple(elts=[binding_expr, binding_info], ctx=ast.Load()))

def wrap_calls(src_code):
    """
    <summary>

    :param src_code:
    :return:
    """
    src_ast = ast.parse(src_code)
    new_ast = CallWrapper().visit(src_ast)
    ast.fix_missing_locations(new_ast)
    new_code = compile(new_ast, filename='<ast>', mode='exec')
    return new_code
