"""
ctxdock.core.compressor
-----------------------
AST-based code compressor that strips function bodies and docstrings
to produce lightweight interface representations for Python files.
"""

import ast


class ASTCompressor(ast.NodeTransformer):
    """AST transformer that removes function bodies and docstrings."""

    def visit_FunctionDef(self, node: ast.FunctionDef) -> ast.FunctionDef:
        """Replace function body with an Ellipsis (...) statement."""
        self.generic_visit(node)
        # Retain arguments/decorator signatures, clear body
        node.body = [ast.Expr(value=ast.Constant(value=...))]
        return node

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> ast.AsyncFunctionDef:
        """Replace async function body with an Ellipsis (...) statement."""
        self.generic_visit(node)
        node.body = [ast.Expr(value=ast.Constant(value=...))]
        return node


class Compressor:
    """Handles code structure compression across supported languages."""

    def compress_python(self, code: str) -> str:
        """
        Parses Python code and returns signature-only definitions.
        If AST parsing fails, returns original code as fallback.
        """
        try:
            tree = ast.parse(code)
            transformer = ASTCompressor()
            modified_tree = transformer.visit(tree)
            ast.fix_missing_locations(modified_tree)
            return ast.unparse(modified_tree)
        except Exception:
            return code

    def compress(self, content: str, file_extension: str, mode: str = "signatures") -> str:
        """
        Compresses source code based on mode and file extension.
        """
        if mode == "none" or not content:
            return content

        if mode == "signatures" and file_extension in [".py", ".pyw"]:
            return self.compress_python(content)

        return content