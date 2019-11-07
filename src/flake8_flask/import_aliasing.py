import ast
from typing import Set, Dict, List

from flake8_flask.constants import MODULE_NAME


class MethodVisitor(ast.NodeVisitor):
    """
    Abstract visitor that tracks call sites across import aliasing
    """

    def __init__(self):
        self.module_alias: str = MODULE_NAME
        self.aliases: Dict[str, str] = {}
        self.module_imports: List[str] = []
        super(MethodVisitor, self).__init__()

    def method_names(self) -> Set[str]:
        """Put all method names you're interested in here"""
        return {"send_file"}

    def visit_Import(self, node: ast.Import) -> None:
        """
        Visits:
            import click
            import click as alias
        """
        for n in node.names:
            self.module_imports.append(n.name)
            if n.name == self.module_alias:
                self.module_alias = n.asname or n.name

    def visit_ImportFrom(self, node: ast.ImportFrom) -> None:
        """
        Visits:
            from click import ...
            from alias import ...
            from alias import ... as ...
        """
        if node.module == self.module_alias:
            self.module_imports.append(node.module)
            for n in node.names:
                if n.name in self.method_names():
                    self.aliases[n.name] = n.asname or n.name

    def is_imported(self, module_name: str):
        return module_name in self.module_imports

    def is_method(self, node: ast.Call, name: str):
        if isinstance(node.func, ast.Attribute):
            if isinstance(node.func.value, ast.Name):
                if node.func.value.id == self.module_alias and node.func.attr == name:
                    return True
        elif isinstance(node.func, ast.Name) and name in self.aliases:
            if node.func.id == self.aliases[name]:
                return True
        return False

    def get_call_keywords(self, d: ast.Call) -> Dict[str, ast.Expr]:
        return dict((keyword.arg, keyword.value) for keyword in d.keywords)

    def get_func_arguments(self, f: ast.FunctionDef) -> List[str]:
        arg_names: List[str] = [arg.arg for arg in f.args.args]
        return arg_names
