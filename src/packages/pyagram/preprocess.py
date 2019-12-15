import ast
import re

from . import banner
from . import pyagram_error
from . import utils

class Preprocessor:
    """
    """

    def __init__(self, code):
        self.code = ast.parse(code)
    
    def preprocess(self):
        self.check_args()
        self.log_lambdas()
        self.wrap_calls()
        ast.fix_missing_locations(self.code)
        self.code = compile(
            self.code,
            filename='<ast>', # TODO: Or perhaps it ought to be '__main__'?
            mode='exec',
        )
    
    def check_args(self):
        arg_checker = ArgChecker()
        arg_checker.visit(self.code)
        if not arg_checker.check_passed:
            raise pyagram_error.PyagramError("Please do not use any parameters prefixed by the string '__pyagram'.")

    def log_lambdas(self):
        lambda_logger = LambdaLogger()
        lambda_logger.visit(self.code)
        lambdas_by_line = lambda_logger.lambdas_by_line
        for lineno in lambdas_by_line:
            sorted_lambdas = sorted(lambdas_by_line[lineno], key=lambda node: node.col_offset)
            for i in range(len(sorted_lambdas)):
                node = sorted_lambdas[i]
                node.args.kwonlyargs.append(ast.arg(f'__pyagram_lambda_{lineno}_{i + 1}'))
                node.args.kw_defaults.append(None)

    def wrap_calls(self):
        self.code = CallWrapper().visit(self.code)

class ArgChecker(ast.NodeVisitor):
    """
    """

    def __init__(self):
        super().__init__()
        self.check_passed = True
    
    def visit_arg(self, node):
        match = re.match('^__pyagram', node.arg)
        if match is not None:
            self.check_passed = False
        self.generic_visit(node)

class LambdaLogger(ast.NodeVisitor):
    """
    """

    def __init__(self):
        super().__init__()
        self.lambdas_by_line = {}
    
    def visit_Lambda(self, node):
        lineno = node.lineno
        if lineno not in self.lambdas_by_line:
            self.lambdas_by_line[lineno] = []
        self.lambdas_by_line[lineno].append(node)
        self.generic_visit(node)

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
            body=banner.Banner(node).banner,
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
            lineno=utils.INNER_CALL_LINENO,
            col_offset=self.id_counter,
        )
        outer_call = ast.Call(
            func=outer_lambda,
            args=[
                inner_call,
                node,
            ],
            keywords=[],
            lineno=utils.OUTER_CALL_LINENO,
            col_offset=self.id_counter,
        )
        self.id_counter += 1 # An outer_call and inner_call correspond to one another iff they have the same ID. (But at the moment we don't actually use that information; we just have it there bc it's nice.)
        self.generic_visit(node)
        return outer_call
