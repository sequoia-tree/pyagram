import ast

from . import banner
from . import constants
from . import utils

class Preprocessor:
    """
    """

    def __init__(self, code):
        self.code = code
        self.num_lines = len(code.split('\n'))
        self.ast = ast.parse(code)
        self.lambdas_by_line = {}

    @property
    def summary(self):
        return (
            self.num_lines,
            {line: len(lambdas) for line, lambdas in self.lambdas_by_line.items()},
        )

    def preprocess(self):
        code_wrapper = CodeWrapper(self)
        self.ast = code_wrapper.visit(self.ast)
        self.encode_lambdas()
        ast.fix_missing_locations(self.ast)
        self.ast = compile(
            self.ast,
            filename=constants.USERCODE_FILENAME,
            mode='exec',
        )

    def encode_lambdas(self):
        for lineno in self.lambdas_by_line:
            sorted_lambdas = sorted(self.lambdas_by_line[lineno], key=lambda node: node.col_offset)
            for i, node in enumerate(sorted_lambdas):
                node.lineno = utils.encode_lineno(
                    node.lineno,
                    i + 1,
                    True,
                    max_lineno=self.num_lines,
                )

class CodeWrapper(ast.NodeTransformer):
    """
    """

    def __init__(self, preprocessor):
        super().__init__()
        self.preprocessor = preprocessor

    def visit_Call(self, node):
        """
        """

        # f(...) --> (lambda banner, call: call)(
        #                (lambda: flag_info)(),
        #                f(...),
        #            )

        inner_lambda = ast.Lambda(
            args=ast.arguments(
                posonlyargs=[],
                args=[],
                vararg=None,
                kwonlyargs=[],
                kwarg=None,
                defaults=[],
                kw_defaults=[],
            ),
            body=banner.Banner(self.preprocessor.code, node).banner,
        )
        outer_lambda = ast.Lambda(
            args=ast.arguments(
                posonlyargs=[],
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
            lineno=utils.encode_lineno(
                node.lineno,
                constants.INNER_CALL_LINENO,
                False,
                max_lineno=self.preprocessor.num_lines,
            ),
        )
        outer_call = ast.Call(
            func=outer_lambda,
            args=[
                inner_call,
                node,
            ],
            keywords=[],
            lineno=utils.encode_lineno(
                node.lineno,
                constants.OUTER_CALL_LINENO,
                False,
                max_lineno=self.preprocessor.num_lines,
            ),
        )
        self.generic_visit(node)
        return outer_call

    def visit_ClassDef(self, node):
        """
        """
        node.lineno = utils.encode_lineno(
            node.lineno,
            constants.CLASS_DEFN_LINENO,
            False,
            max_lineno=self.preprocessor.num_lines,
        )
        self.generic_visit(node)
        return node

    def visit_Lambda(self, node):
        """
        """
        lineno = node.lineno
        if lineno not in self.preprocessor.lambdas_by_line:
            self.preprocessor.lambdas_by_line[lineno] = []
        self.preprocessor.lambdas_by_line[lineno].append(node)
        self.generic_visit(node)
        return node

    def visit_ListComp(self, node):
        """
        """
        node.lineno = utils.encode_lineno(
            node.lineno,
            constants.GENXP_COMP_LINENO,
            False,
            max_lineno=self.preprocessor.num_lines,
        )
        self.generic_visit(node)
        return node

    def visit_SetComp(self, node):
        """
        """
        node.lineno = utils.encode_lineno(
            node.lineno,
            constants.GENXP_COMP_LINENO,
            False,
            max_lineno=self.preprocessor.num_lines,
        )
        self.generic_visit(node)
        return node

    def visit_DictComp(self, node):
        """
        """
        node.lineno = utils.encode_lineno(
            node.lineno,
            constants.GENXP_COMP_LINENO,
            False,
            max_lineno=self.preprocessor.num_lines,
        )
        self.generic_visit(node)
        return node
