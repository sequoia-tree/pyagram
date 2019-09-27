import ast
import astunparse

INNER_CALL_LINENO = -1
OUTER_CALL_LINENO = -2

class CallWrapper(ast.NodeTransformer):
    """
    <summary>
    """

    def __init__(self, code):
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

        # ----------------------------------------------------------------------

        func_code = astunparse.unparse(node.func)
        func_call_bitmap = isinstance(node.func, ast.Call)
        args_code = ast.Tuple(
            elts=[
                ? if isinstance(arg, ast.Starred) else ast.Str(astunparse.unparse(arg)) # TODO: If arg is an ast.Starred instance then pass along a PyagramError so that in the box where the value of the *arg would go, you can display a red error message with a link to the Issue on the Pyagram GitHub.
                for arg in node.args
            ],
            ctx=ast.Load(),
        )
        args_call_bitmap = ast.Tuple(
            elts=[
                ast.NameConstant(isinstance(arg, ast.Call))
                for arg in node.args
            ],
            ctx=ast.Load(),
        )
        kwargs_code = ast.Tuple(
            elts=[
                ? if kwarg.arg is None else ast.Tuple(elts=[ast.Str(kwarg.arg), ast.Str(astunparse.unparse(kwarg.value))], ctx=ast.Load()) # TODO: If kwarg.arg is None then it's something like `**kwargs` rather than `a=1` or `b=2`. We can't handle that case, so pass along a PyagramError so that in the box where the value of `**kwargs` would go, you can display a red error message with a link to the Issue on the Pyagram GitHub.
                for kwarg in node.keywords
            ],
            ctx=ast.Load(),
        )
        kwargs_call_bitmap = ast.Tuple(
            elts=[
                ast.NameConstant(isinstance(kwarg.value, ast.Call))
                for kwarg in node.keywords
            ],
            ctx=ast.Load(),
        )
        flag_info = ast.Tuple(
            elts=[
                func_code,
                func_call_bitmap,
                args_code,
                args_call_bitmap,
                kwargs_code,
                kwargs_call_bitmap,
            ],
            ctx=ast.Load(),
        )
        inner_lambda = ast.Lambda(
            args=ast.arguments(
                args=[],
                vararg=None,
                kwonlyargs=[],
                kwarg=None,
                defaults=[],
                kw_defaults=[],
            ),
            body=flag_info,
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

        self.id_counter += 1
        # outer_call:
        #   lineno = -1
        #   col_offset = id # I guess we won't use the ID. But it's nice to have.
        # inner_call:
        #   lineno = -2
        #   col_offset = id # I guess we won't use the ID. But it's nice to have.
        # So an outer_call and inner_call correspond to one another iff they have the same ID.

        self.generic_visit(node)
        return outer_call

def wrap_calls(src_code):
    """
    <summary>

    :param src_code:
    :return:
    """
    src_ast = ast.parse(src_code)
    new_ast = CallWrapper(src_code).visit(src_ast)
    ast.fix_missing_locations(new_ast)
    new_code = compile(new_ast, filename='<ast>', mode='exec')
    return new_code
