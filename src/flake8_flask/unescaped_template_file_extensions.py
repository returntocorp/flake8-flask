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


fxn_name: str = "render_template"
escaped_extensions: Set[str] = {"html", "htm", "xml", "xhtml"}
escape_function_names: Set[str] = {"escape"}


class UnescapedTemplateFileExtensionsVisitor(FlaskBaseVisitor):
    name = "r2c-unescaped-template-file-extension"

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

    def visit_Call(self, call_node: ast.Call):
        # Is this flask.render_template?
        if not self.is_method(call_node, fxn_name):
            logger.debug(f"This call is not {fxn_name}")
            return

        # Check if the possible values aren't an autoescape extension
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

        logger.debug(f"Found this node: {ast.dump(call_node)}")
        extensions = set(
            [self._get_template_extension(value) for value in possible_values]
        )
        extensions_to_go_in_message = extensions - escaped_extensions
        self.report_nodes.append(
            {
                "node": call_node,
                "message": f"{self.name} Flask does not autoescape templates with the {str(extensions_to_go_in_message)} extension by default. Flask only autoescapes .html, .htm, .xml, and .xhtml files. If you want to use this extension, make sure your variables are escaped using `flask.Markup.escape`. If you are sure your variables are safe, you can disable this line by adding the comment #noqa {self.name}.",
            }
        )
