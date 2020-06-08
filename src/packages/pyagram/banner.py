import ast

from . import constants

class Banner:
    """
    """

    def __init__(self, code, node):
        self.code = code
        self.node = node
        self.elements = []

    @property
    def summary(self):
        """
        """
        return ast.Tuple(
            elts=[
                ast.Constant(
                    value=self.node.col_offset,
                    kind=None,
                ),
                ast.List(
                    elts=self.elements,
                    ctx=ast.Load(),
                ),
            ],
            ctx=ast.Load(),
        )

    def source(self, node):
        return ast.get_source_segment(self.code, node).strip('\n')

class FunctionCallBanner(Banner):
    """
    """

    def __init__(self, code, node):
        super().__init__(code, node)
        self.binding_index = 0
        self.add_func_info(node.func)
        self.add_args_info(node.args)
        self.add_kwds_info(node.keywords)

    def add_func_info(self, func):
        """
        """
        if isinstance(func, ast.Lambda):
            self.add_bindings(func, constants.NORMAL_ARG, code_prefix='(', code_suffix=')')
        else:
            self.add_bindings(func, constants.NORMAL_ARG)

    def add_args_info(self, args):
        """
        """
        for arg in args:
            is_unpacked = isinstance(arg, ast.Starred)
            self.add_bindings(
                arg,
                constants.SINGLY_UNPACKED_ARG if is_unpacked else constants.NORMAL_ARG,
            )

    def add_kwds_info(self, keywords):
        """
        """
        for keyword in keywords:
            is_unpacked = keyword.arg is None
            self.add_bindings(
                keyword.value,
                constants.DOUBLY_UNPACKED_ARG if is_unpacked else constants.NORMAL_ARG,
                code_prefix='**' if is_unpacked else f'{keyword.arg}=',
                keyword=keyword.arg,
            )

    def add_bindings(self, node, unpacking_code, *, keyword=None, code_prefix=None, code_suffix=None):
        """
        """
        code = self.source(node)
        if code_prefix is not None:
            code = ''.join((code_prefix, code))
        if code_suffix is not None:
            code = ''.join((code, code_suffix))
        self.elements.append(ast.Tuple(
            elts=[
                ast.Constant(
                    value=code,
                    kind=None,
                ),
                ast.Constant(
                    value=keyword,
                    kind=None,
                ),
                ast.Constant(
                    value=self.binding_index,
                    kind=None,
                ),
                ast.Constant(
                    value=unpacking_code,
                    kind=None,
                ),
            ],
            ctx=ast.Load(),
        ))
        self.binding_index += 1

class ComprehensionBanner(Banner):
    """
    """

    def __init__(self, code, node):
        super().__init__(code, node)
        self.add_comp_info(node)

    def add_comp_info(self, comprehension):
        """
        """
        self.elements.append(
            ast.Constant(
                value=self.source(comprehension),
                kind=None,
            )
        )
