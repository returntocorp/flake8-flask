import ast
import logging
from flake8_flask.flask_base_visitor import FlaskBaseVisitor
from typing import Any, Dict, Iterator, List, Optional, Set, Tuple


logger = logging.getLogger(__file__)
# Note that this is not cyclomatic complexity
# Complexity is defined as the string length of the code
COMPLEXITY_THRESHOLD = 500
class FlaskMethodVisitor(FlaskBaseVisitor):
    """
    Abstract visitor that visits Flask calls
    """

    def __init__(self):
        self.flask_alias: str = "flask"
        self.aliases: Dict[str, str] = {}
        self.app_alias: str = "app"
        super().__init__()



    def method_names(self) -> Set[str]:
        pass

    def visit_Import(self, node: ast.Import) -> None:
        """
        Visits:
            import flask
            import flask as alias
        """
        for n in node.names:
            if n.name == self.flask_alias:
                self.flask_alias = n.asname or n.name

    def visit_ImportFrom(self, node: ast.ImportFrom) -> None:
        """
        Visits:
            from flask import ...
            from alias import ...
            from alias import ... as ...
        """
        if node.module == self.flask_alias:
            for n in node.names:
                if n.name in self.method_names():
                    self.aliases[n.name] = n.asname or n.name

    def visit_Assign(self, node: ast.Assign) -> None:
        if isinstance(node.value, ast.Call):
            if self.get_call_func_name(node.value) == "Flask":
                self.app_alias = node.targets[0].id

    def is_method(self, node: ast.Call, name: str):
        if isinstance(node.func, ast.Attribute):
            # flask module imported
            if isinstance(node.func.value, ast.Name):
                if node.func.value.id == self.app_alias and node.func.attr == name:
                    return True
        elif isinstance(node.func, ast.Name) and name in self.aliases:
            # method imported from flask
            if node.func.id == self.aliases[name]:
                return True
        return False

    def get_call_keywords(self, d: ast.Call) -> Dict[str, ast.Expr]:
        return dict((keyword.arg, keyword.value) for keyword in d.keywords)

    def get_call_func_name(self, d: ast.Call) -> str:
        return d.func.id

    def get_func_arguments(self, f: ast.FunctionDef) -> List[str]:
        arg_names: List[str] = [arg.arg for arg in f.args.args]
        return arg_names



class FlaskDecoratorVisitor(FlaskMethodVisitor):
    METHOD_NAMES: Set[str] = {"route"}

    def __init__(self):
        super().__init__()

    def method_names(self) -> Set[str]:
        return FlaskDecoratorVisitor.METHOD_NAMES.copy()

    def is_flask_route(self, d: ast.Call):
        return self.is_method(d, "route")

    def flask_route_decorators(self, node: ast.FunctionDef) -> Iterator[ast.Call]:
        for decorator in node.decorator_list:
            if not isinstance(decorator, ast.Call):
                continue
            elif self.is_flask_route(decorator):
                yield decorator

class AppRouteVisitor(FlaskDecoratorVisitor):
    name = "r2c-flask-use-blueprint-for-modularity"

    def visit_FunctionDef(self, f: ast.FunctionDef) -> None:
        """
        Visits each function checking for if its cli.command. If so,
        verifies the options have default and help text
        """
        for d in self.flask_route_decorators(f):
            if self.module_has_high_complexity(f):
                self.report_nodes.append({
                    "node": d,
                    "message": f"{self.name} Consider using Blueprint for modularity. See https://flask.palletsprojects.com/en/1.1.x/blueprints/#blueprints"
                   })


    def module_has_high_complexity(self, f: ast.FunctionDef) -> bool:
        complexity = len(str(ast.dump(f)))
        return complexity > COMPLEXITY_THRESHOLD
