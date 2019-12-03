import ast
from collections import defaultdict
from typing import Dict, List, Set

from flake8_flask.constants import MODULE_NAME


class MethodVisitor(ast.NodeVisitor):
    """
    Abstract visitor that tracks call sites across import aliasing
    """

    def __init__(self):
        self.module_alias: str = MODULE_NAME
        self.methods: Dict[str, List[str]] = defaultdict(list)
        self.module_aliases: Dict[str, str] = {}
        self.method_aliases: Dict[str, Dict[str, List]] = defaultdict(dict)
        self.modules: Set[str] = set()
        super(MethodVisitor, self).__init__()

    def method_names(self) -> Set[str]:
        """Put all method names you're interested in here"""
        return {"send_file", "render_template"}

    def visit_Import(self, node: ast.Import) -> None:
        """
        Visits:
            import click
            import click as alias
        """
        for n in node.names:
            self.modules.add(n.name)
            self.module_aliases[n.name] = n.asname or n.name

    def visit_ImportFrom(self, node: ast.ImportFrom) -> None:
        """
        Visits:
            from click import ...
            from alias import ...
            from alias import ... as ...
        """
        self.modules.add(node.module)
        self.methods[node.module].extend([n.name for n in node.names])
        for n in node.names:
            self.method_aliases[node.module][n.name] = n.asname or n.name

    def is_imported(self, module_name: str) -> bool:
        return module_name in self.modules

    def is_method_of(self, fxn_name: str, module_name: str) -> bool:
        return fxn_name in self.methods.get(module_name, [])

    def is_method_alias_of(self, fxn_name: str, original_fxn_name: str, module_name: str) -> bool:
        return fxn_name == self.method_aliases.get(module_name, {}).get(original_fxn_name, "")

    def is_method(self, node: ast.Call, name: str) -> bool:
        if isinstance(node.func, ast.Attribute):
            if isinstance(node.func.value, ast.Name):
                if node.func.value.id == self.module_aliases.get(node.func.value.id) and node.func.attr == name:
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
