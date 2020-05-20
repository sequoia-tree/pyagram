import ast

from . import constants

class Banner:
    """
    """

    def __init__(self, code, node):
        self.code = code
        self.elements = []
        self.val_idx = 0 # TODO: Rename
        self.add_func_info(node.func)
        self.add_args_info(node.args)
        self.add_kwds_info(node.keywords)
        self.elements = ast.List(
            elts=self.elements,
            ctx=ast.Load(),
        )

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
                kwd=keyword.arg,
            )

    def add_bindings(self, node, unpacking_code, *, kwd=None, code_prefix=None, code_suffix=None):
        """
        """
        code = ast.get_source_segment(self.code, node).strip('\n')
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
                    value=kwd,
                    kind=None,
                ),
                ast.Constant(
                    value=self.val_idx,
                    kind=None,
                ),
                ast.Constant(
                    value=unpacking_code,
                    kind=None,
                ),
            ],
            ctx=ast.Load(),
        ))
        self.val_idx += 1
