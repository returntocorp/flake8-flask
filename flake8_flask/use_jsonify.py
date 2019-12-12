import ast
import logging
import sys
from typing import List, Optional, Set

from flake8_flask.constants import MODULE_NAME
from flake8_flask.flask_base_visitor import FlaskBaseVisitor

logger = logging.getLogger(__file__)
logger.setLevel(logging.INFO)
handler = logging.StreamHandler(stream=sys.stderr)
handler.setFormatter(
    logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
)
logger.addHandler(handler)

JSON_MODULE_NAME = "json"


class JsonifyVisitor(FlaskBaseVisitor):
    name = "r2c-flask-use-jsonify"

    def _get_function_def_node(
        self, return_node: ast.Return
    ) -> Optional[ast.FunctionDef]:
        cursor = return_node
        while not isinstance(cursor, ast.Module):
            cursor = cursor.r2c_parent
            if isinstance(cursor, ast.FunctionDef):
                return cursor
        return None

    def _is_function_def_flask_route(self, function_def_node: ast.FunctionDef) -> bool:
        if not self.is_imported("flask"):
            return False

        for decorator in function_def_node.decorator_list:
            if isinstance(decorator, ast.Call) and isinstance(
                decorator.func, ast.Attribute
            ):
                if decorator.func.attr == "route":
                    return True
        return False

    def _is_call_json_dumps(self, call_node: ast.Call) -> bool:
        if isinstance(call_node.func, ast.Attribute) and call_node.func.attr == "dumps":
            if (
                isinstance(call_node.func.value, ast.Name)
                and call_node.func.value.id == "json"
            ):
                return True
        elif isinstance(call_node.func, ast.Name):
            return self.is_method_alias_of(call_node.func.id, "dumps", "json")
        return False

    def visit_Return(self, return_node: ast.Return):
        # Check if return value is a Call node
        if not isinstance(return_node.value, ast.Call):
            logger.debug("Return value is not a call node, aborting.")
            return

        # See if this is returning `json.dumps`
        call_node = return_node.value
        if not self._is_call_json_dumps(call_node):
            logger.debug("Not returning json.dumps, don't care.")
            return
        # Go back up to see if FunctionDef has a flask route decorator
        function_def_node = self._get_function_def_node(return_node)
        if not function_def_node:
            logger.debug(
                "Could not get the function definition associated with this return. Maybe it's async?"
            )
            return

        if not self._is_function_def_flask_route(function_def_node):
            logger.debug("Function is not a Flask route")
            return

        logger.debug(f"Found this node: {ast.dump(return_node)}")
        self.report_nodes.append(
            {
                "node": return_node,
                "message": f"{self.name} Use `flask.jsonify()` instead of `json.dumps()` when returning JSON from Flask routes. `flask.jsonify()` is a helper method which handles the correct settings for returning JSON.",
            }
        )
