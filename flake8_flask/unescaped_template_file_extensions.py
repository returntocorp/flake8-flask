import ast
import logging
import sys
from typing import List, Set

from flake8_flask.constants import MODULE_NAME
from flake8_flask.flask_base_visitor import FlaskBaseVisitor

logger = logging.getLogger(__file__)
logger.setLevel(logging.INFO)
handler = logging.StreamHandler(stream=sys.stderr)
handler.setFormatter(
    logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
)
logger.addHandler(handler)


FXN_NAME: str = "render_template"
escaped_extensions: Set[str] = {"html", "htm", "xml", "xhtml"}
escape_function_names: Set[str] = {"escape"}


class UnescapedTemplateFileExtensionsVisitor(FlaskBaseVisitor):
    def __init__(self, include_edge_cases=False):
        self.include_edge_cases = include_edge_cases
        super(UnescapedTemplateFileExtensionsVisitor, self).__init__()

    name = "r2c-flask-unescaped-file-extension"

    def _get_template_extension(self, template_name: str) -> str:
        splits: List[str] = template_name.split(".")
        extension: str = splits[-1] if len(splits) > 1 else ""
        return extension

    def _has_escaped_extension(self, template_name: str) -> bool:
        extension: str = self._get_template_extension(template_name)
        if extension in escaped_extensions:
            return True
        return False

    def _resolve_to_possible_values(self, node) -> List[str]:
        if isinstance(node, ast.Str):
            return [node.s]
        elif isinstance(node, ast.Name):
            return self._get_possible_symbol_values(node.id)
        else:
            return ""

    def _is_kwarg_escaped(self, keyword) -> bool:
        if not isinstance(keyword.value, ast.Call):
            return False
        fxn = keyword.value.func
        if isinstance(fxn, ast.Attribute):
            return fxn.attr in escape_function_names
        elif isinstance(fxn, ast.Name):
            return fxn.id in escape_function_names

    def _edge_case_detect_return_content_type_with_text(
        self, call_node: ast.Call
    ) -> bool:
        """
        Detects if this call to `render_template` is in a return
        and that the third return element is a dict that contains
        {"content-type": "text/plain"}. Flask routes can exhibit
        this behavior, and if the template is rendered as "text/plain"
        we assume it is safe.
        """
        if isinstance(call_node.r2c_parent, ast.Tuple):
            if isinstance(call_node.r2c_parent.r2c_parent, ast.Return):
                return_value_tuple_node = call_node.r2c_parent
                headers_dict_node = return_value_tuple_node.elts[2]
                for i, key in enumerate(headers_dict_node.keys):
                    if isinstance(key, ast.Str) and key.s.lower() == "content-type":
                        if isinstance(headers_dict_node.values[i], ast.Str):
                            return headers_dict_node.values[i].s.lower() == "text/plain"
        return False

    def visit_Call(self, call_node: ast.Call):
        # Is this flask.render_template?
        if not self.is_node_method_alias_of(call_node, FXN_NAME, MODULE_NAME):
            logger.debug(f"This call is not {FXN_NAME}")
            return

        # Check if the possible values aren't an autoescape extension
        logger.debug(ast.dump(call_node))
        arg0 = call_node.args[0]
        possible_values = self._resolve_to_possible_values(arg0)
        logger.debug(possible_values)
        if all([self._has_escaped_extension(value) for value in possible_values]):
            logger.debug(
                "Template has an escaped extension; template will be autoescaped"
            )
            return

        # If not autoescaped, check for escaped vars
        if all([self._is_kwarg_escaped(kw) for kw in call_node.keywords]):
            logger.debug("All context variables are escaped.")
            return

        # Edge cases
        if self.include_edge_cases:
            if self._edge_case_detect_return_content_type_with_text(call_node):
                logger.debug(
                    "Template is rendered with `text/plain` mimetype. Assuming this is safe."
                )
                return

        logger.debug(f"Found this node: {ast.dump(call_node)}")
        extensions = set(
            [self._get_template_extension(value) for value in possible_values]
        )
        extensions_to_go_in_message = extensions - escaped_extensions
        self.report_nodes.append(
            {
                "node": call_node,
                "message": f"{self.name} Flask does not autoescape templates with the {str(extensions_to_go_in_message)} extension by default. Flask only autoescapes .html, .htm, .xml, and .xhtml files. Make sure your variables are escaped using `flask.Markup.escape`.",
            }
        )
