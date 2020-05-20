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
        """
        """
        return (
            self.num_lines,
            {line: len(lambdas) for line, lambdas in self.lambdas_by_line.items()},
        )

    def preprocess(self):
        """
        """
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
        """
        """
        for lineno in self.lambdas_by_line:
            sorted_lambdas = sorted(self.lambdas_by_line[lineno], key=lambda node: node.col_offset)
            for i, node in enumerate(sorted_lambdas):
                node.lineno = utils.encode_lineno(
                    node.lineno,
                    i + 1,
                    True,
                    max_lineno=self.num_lines,
                )

    def wrap_node(self, frame_code, return_node, *, lineno=None, params=[], args=[], keywords=[]):
        """
        """
        if lineno is None:
            lineno = return_node.lineno
        function = ast.Lambda(
            args=ast.arguments(
                posonlyargs=params,
                args=[],
                vararg=None,
                kwonlyargs=[],
                kwarg=None,
                defaults=[],
                kw_defaults=[],
            ),
            body=return_node,
        )
        function_call = ast.Call(
            func=function,
            args=args,
            keywords=keywords,
            lineno=utils.encode_lineno(
                lineno,
                frame_code,
                False,
                max_lineno=self.num_lines,
            ),
        )
        return function_call

class CodeWrapper(ast.NodeTransformer):
    """
    """

    def __init__(self, preprocessor):
        super().__init__()
        self.preprocessor = preprocessor

    def visit_Call(self, node):
        """
        """

        # f(x, y, z) --> (lambda info, call: call)( # wrapper
        #                    (lambda: flag_info)(), # banner
        #                    (lambda: f)()(         # function
        #                        (lambda: x)(),     # arg
        #                        (lambda: y)(),     # arg
        #                        (lambda: z)(),     # arg
        #                    ),
        #                )

        banner_call = self.preprocessor.wrap_node(
            constants.INNER_CALL_LINENO,
            banner.Banner(self.preprocessor.code, node).elements,
            lineno=node.lineno,
        )
        function_call = ast.Call(
            func=self.preprocessor.wrap_node(
                constants.FN_WRAPPER_LINENO,
                node.func,
            ),
            args=[
                (
                    ast.Starred(
                        value=self.preprocessor.wrap_node(
                            constants.RG_WRAPPER_LINENO,
                            arg.value,
                        ),
                        ctx=ast.Load(),
                    )
                    if isinstance(arg, ast.Starred)
                    else self.preprocessor.wrap_node(
                        constants.RG_WRAPPER_LINENO,
                        arg,
                    )
                )
                for arg in node.args
            ],
            keywords=[
                ast.keyword(
                    arg=keyword.arg,
                    value=self.preprocessor.wrap_node(
                        constants.RG_WRAPPER_LINENO,
                        keyword.value,
                    )
                )
                for keyword in node.keywords
            ],
            lineno=node.lineno,
        )
        wrapper_call = self.preprocessor.wrap_node(
            constants.OUTER_CALL_LINENO,
            ast.Name(id='call', ctx=ast.Load()),
            lineno=node.lineno,
            params=[
                ast.arg(arg='info', annotation=None),
                ast.arg(arg='call', annotation=None),
            ],
            args=[
                banner_call,
                function_call,
            ],
        )
        self.generic_visit(node)
        return wrapper_call

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
            constants.CNTNR_COMP_LINENO,
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
            constants.CNTNR_COMP_LINENO,
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
            constants.CNTNR_COMP_LINENO,
            False,
            max_lineno=self.preprocessor.num_lines,
        )
        self.generic_visit(node)
        return node
