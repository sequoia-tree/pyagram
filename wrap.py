import ast

INNER_CALL_LINENO = -1
OUTER_CALL_LINENO = -2

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



        argument_code = ast.Tuple( # TODO: The code the student passes in for each arg.
            elts=[],
            ctx=ast.Load(),
        )
        call_bitmap = ast.Tuple( # TODO: Which args are calls vs directly evaluated.
            elts=[], # TODO
            ctx=ast.Load(), # TODO: You also need to know whether the function is the result of a call not.
        )
        # TODO: NOTE: For f(a, b=c, *d, **e) you'd get ...
        # args = [
        #            Name(id='a', ctx=Load()),
        #            Starred(value=Name(id='d', ctx=Load()), ctx=Load())
        #        ],
        # keywords = [
        #     keyword(arg='b', value=Name(id='c', ctx=Load())),
        #     keyword(arg=None, value=Name(id='e', ctx=Load()))
        # ]



        flag_info = ast.Tuple(
            elts=[argument_code, call_bitmap],
            ctx=ast.Load()
        )
        flag_info = ast.NameConstant(None)


        # TODO: Maybe call them precursor_function, precursor_call, successor_function, and successor_call, instead of inner_lambda, inner_call, outer_lambda, and outer_call? Or work "wrapped" or "wrap" into the variable names?
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

        self.generic_visit(node)

        # TODO: Are there nodes other than Call nodes (eg listcomp, dictcomp, etc) that create their own frames? If so, we need to mutate those too. And also flag_info bitmap should account for them too (not just Call nodes).

        return outer_call

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
