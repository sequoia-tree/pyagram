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
        self.new_node_linenos = []
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
        self.update_linenos()
        self.encode_lambdas()
        ast.fix_missing_locations(self.ast)
        self.ast = compile(
            self.ast,
            filename=constants.USERCODE_FILENAME,
            mode='exec',
        )

    def update_linenos(self):
        """
        """
        while 0 < len(self.new_node_linenos):
            node, step_code = self.new_node_linenos.pop(0)
            node.lineno = utils.encode_lineno(
                node.lineno,
                step_code,
                False,
                max_lineno=self.num_lines,
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

class CodeWrapper(ast.NodeTransformer):
    """
    """

    def __init__(self, preprocessor):
        super().__init__()
        self.preprocessor = preprocessor

    def mod_lineno(self, node, step_code):
        """
        """
        self.preprocessor.new_node_linenos.append((node, step_code))

    def visit_Call(self, node):
        """
        """

        # f(x, y, z) --> (lambda info, call: call)( # wrapper
        #                    (lambda: info)(),      # banner
        #                    (lambda: f)()(         # function
        #                        (lambda: x)(),     # arg
        #                        (lambda: y)(),     # arg
        #                        (lambda: z)(),     # arg
        #                    ),
        #                )

        banner_call = self.insert_eager_call(
            node.lineno,
            constants.INNER_CALL_LINENO,
            banner.FunctionCallBanner(self.preprocessor.code, node).summary,
        )
        self.generic_visit(node)
        function_call = ast.Call(
            func=self.insert_eager_call(
                node.func.lineno,
                constants.FN_WRAPPER_LINENO,
                node.func,
            ),
            args=[
                (
                    ast.Starred(
                        value=self.insert_lazy_call(
                            arg.value.lineno,
                            constants.RG_WRAPPER_LINENO,
                            ('arg', arg.value),
                        ),
                        ctx=ast.Load(),
                    )
                    if isinstance(arg, ast.Starred)
                    else self.insert_lazy_call(
                        arg.lineno,
                        constants.RG_WRAPPER_LINENO,
                        ('arg', arg),
                    )
                )
                for arg in node.args
            ],
            keywords=[
                ast.keyword(
                    arg=keyword.arg,
                    value=self.insert_lazy_call(
                        keyword.value.lineno,
                        constants.RG_WRAPPER_LINENO,
                        ('arg', keyword.value),
                    )
                )
                for keyword in node.keywords
            ],
            lineno=node.lineno,
        )
        wrapper_call = self.insert_lazy_call(
            node.lineno,
            constants.OUTER_CALL_LINENO,
            ('info', banner_call),
            ('call', function_call),
        )
        return wrapper_call

    def visit_ClassDef(self, node):
        """
        """
        self.generic_visit(node)
        self.mod_lineno(node, constants.CLASS_DEFN_LINENO)
        return node

    def visit_Lambda(self, node):
        """
        """
        self.generic_visit(node)
        lineno = node.lineno
        if lineno not in self.preprocessor.lambdas_by_line:
            self.preprocessor.lambdas_by_line[lineno] = []
        self.preprocessor.lambdas_by_line[lineno].append(node)
        return node

    def visit_ListComp(self, node):
        """
        """

        # [x for y in z] --> (lambda info, comp: comp)( # wrapper
        #                        (lambda: info)(),      # banner
        #                        [x for y in z]         # comp
        #                    )

        banner_call = self.insert_eager_call(
            node.lineno,
            constants.INNER_COMP_LINENO,
            banner.ComprehensionBanner(self.preprocessor.code, node).summary,
        )
        self.generic_visit(node)
        wrapper_call = self.insert_lazy_call(
            node.lineno,
            constants.CNTNR_COMP_LINENO,
            ('info', banner_call),
            ('comp', node),
        )
        return wrapper_call

    def visit_SetComp(self, node):
        """
        """
        return self.visit_ListComp(node)

    def visit_DictComp(self, node):
        """
        """
        return self.visit_ListComp(node)

    def insert_call(self, lineno, step_code, return_node, *, params, args):
        """
        """
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
            keywords=[],
            lineno=lineno,
        )
        self.mod_lineno(function_call, step_code)
        return function_call

    def insert_eager_call(self, lineno, step_code, return_node):
        """
        """
        return self.insert_call(
            lineno,
            step_code,
            return_node,
            params=[],
            args=[],
        )

    def insert_lazy_call(self, lineno, step_code, *bindings):
        """
        """
        params, args = zip(*bindings)
        return_param = params[-1]
        return self.insert_call(
            lineno,
            step_code,
            ast.Name(id=return_param, ctx=ast.Load()),
            params=[
                ast.arg(arg=param, annotation=None)
                for param in params
            ],
            args=list(args),
        )
