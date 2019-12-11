import ast
import logging
import os
from collections import defaultdict
from flake8_flask.flask_base_visitor import FlaskBaseVisitor
from typing import Any, Dict, Iterator, List, Optional, Set, Tuple


logger = logging.getLogger(__file__)
ROUTE_COUNTER_THRESHOLD = 3

class FlaskMethodVisitor(FlaskBaseVisitor):
    """
    Abstract visitor that visits Flask calls
    """

    def __init__(self):
        self.app_alias: str = "app"
        super().__init__()

    def visit_Assign(self, node: ast.Assign) -> None:
        if isinstance(node.value, ast.Call):
            # assume function call Flask() is the app alias
            if self.get_call_func_name(node.value) == "Flask":
                self.app_alias = node.targets[0].id

    def is_method(self, node: ast.Call, name: str):
        if isinstance(node.func, ast.Attribute):
            # save flask  app initialization as alias
            if isinstance(node.func.value, ast.Name):
                if node.func.value.id == self.app_alias and node.func.attr == name:
                    return True
        return False

    def get_call_keywords(self, d: ast.Call) -> Dict[str, ast.Expr]:
        return dict((keyword.arg, keyword.value) for keyword in d.keywords)

    def get_call_func_name(self, d: ast.Call) -> str:
        if isinstance(d.func, ast.Attribute):
            if isinstance(d.func.value, ast.Name):
                return d.func.value.id
            elif isinstance(d.func.value, ast.Str):
                return d.func.value.s
            return ""
        elif isinstance(d.func, ast.Name):
            return d.func.id
        return ""

    def get_func_arguments(self, f: ast.FunctionDef) -> List[str]:
        arg_names: List[str] = [arg.arg for arg in f.args.args]
        return arg_names



class FlaskDecoratorVisitor(FlaskMethodVisitor):
    def __init__(self):
        super().__init__()

    def is_flask_route(self, d: ast.Call):
        return self.is_method(d, "route")

    def flask_route_decorators(self, node: ast.FunctionDef) -> Iterator[ast.Call]:
        for decorator in node.decorator_list:
            if not isinstance(decorator, ast.Call):
                continue
            elif self.is_flask_route(decorator):
                yield decorator
    def get_route_from_decorator(self, decorator):
        if not isinstance(decorator, ast.Call):
            return
        if not decorator.args:
            return
        # URL is the first argument
        route_arg = decorator.args[0]
        if isinstance(route_arg, ast.Str):
            return route_arg.s
        else:
            return
class AppRouteVisitor(FlaskDecoratorVisitor):
    name = "r2c-flask-use-blueprint-for-modularity"
    # each flask app has a counter
    route_counter: Dict[str, Dict[str, int]] = {}

    def __init__(self, filename: str):
        self.filename = filename
        self.route_counter[filename] = defaultdict(int)
        super().__init__()

    def visit_FunctionDef(self, f: ast.FunctionDef) -> None:
        """
        Visits each function checking for if its cli.command. If so,
        verifies the options have default and help text
        """
        for d in self.flask_route_decorators(f):
            route = self.get_route_from_decorator(d)
            self.route_counter[self.filename][route] += 1
            route_prefix = os.path.split(route)[0]
            if self.route_occurs_often(route_prefix):
                self.report_nodes.append({
                    "node": d,
                    "message": f"{self.name} Consider using Blueprint for routes with `{route_prefix}`. Blueprint make applications modular and simple. See https://flask.palletsprojects.com/en/1.1.x/blueprints/#blueprints"
                   })

    def route_occurs_often(self, route_prefix: str) -> bool:
        if route_prefix == '/':
            return False
        counter = 0
        for k, v in self.route_counter[self.filename].items():
            if k.startswith(route_prefix):
                counter += v
        return counter >= ROUTE_COUNTER_THRESHOLD