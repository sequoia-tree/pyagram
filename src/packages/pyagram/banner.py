import ast

from . import constants

OPEN_PARENTHESIS, CLOSE_PARENTHESIS = ast.Str('('), ast.Str(')')
OPEN_STARRED_LIST, CLOSE_STARRED_LIST = ast.Str('*['), ast.Str(']')
OPEN_STARRED_TUPLE, CLOSE_STARRED_TUPLE = ast.Str('*('), ast.Str(')')
OPEN_KEYWORD_DICT, CLOSE_KEYWORD_DICT = ast.Str('**{'), ast.Str('}')
# TODO: Do you still need this stuff?
COMMA = ast.Str(', ')

class Banner:
    """
    """

    def __init__(self, code, node):
        self.code = code
        self.symbols = []
        self.val_idx = 0
        self.has_prev_input = False
        self.add_func_info(node.func)
        self.symbols.append(OPEN_PARENTHESIS)
        self.add_args_info(node.args)
        self.add_kwds_info(node.keywords)
        self.symbols.append(CLOSE_PARENTHESIS)
        self.symbols = ast.List(
            elts=self.symbols,
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
            if self.has_prev_input:
                self.symbols.append(COMMA)
            is_unpacked = isinstance(arg, ast.Starred)
            self.add_bindings(
                arg,
                constants.SINGLY_UNPACKED_ARG if is_unpacked else constants.NORMAL_ARG,
            )
            self.has_prev_input = True

    def add_kwds_info(self, keywords):
        """
        """
        for keyword in keywords:
            is_unpacked = keyword.arg is None
            if not is_unpacked:
                self.symbols.append(ast.Str(f'{keyword.arg}='))
            self.add_bindings(
                keyword.value,
                constants.DOUBLY_UNPACKED_ARG if is_unpacked else constants.NORMAL_ARG,
            )
            self.has_prev_input = True

    def add_bindings(self, node, unpacking_code, *, code_prefix=None, code_suffix=None):
        """
        """
        code = ast.get_source_segment(self.code, node).strip('\n')
        if code_prefix is not None:
            code = ''.join((code_prefix, code))
        if code_suffix is not None:
            code = ''.join((code, code_suffix))
        self.symbols.append(ast.Tuple(
            elts=[
                ast.Constant(
                    value=code,
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
