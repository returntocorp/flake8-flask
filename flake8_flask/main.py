import ast
import logging
import sys

from flake8_flask import __version__
from flake8_flask.secure_set_cookies import SecureSetCookiesVisitor
from flake8_flask.send_file_checks import SendFileChecksVisitor
from flake8_flask.unescaped_template_file_extensions import (
    UnescapedTemplateFileExtensionsVisitor,
)
from flake8_flask.use_jsonify import JsonifyVisitor
from flake8_flask.upsell_blueprint import AppRouteVisitor

logger = logging.getLogger(__file__)
logger.setLevel(logging.INFO)
handler = logging.StreamHandler(stream=sys.stderr)
handler.setFormatter(
    logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
)
logger.addHandler(handler)


class Flake8Flask:
    name = "flake8-flask"
    version = __version__
    child_to_parent = {}

    def __init__(self, tree, filename, add_parents=True):
        self.tree = tree
        self.filename = filename
        # # Add in parent nodes to tree
        if add_parents:
            for node in ast.walk(self.tree):
                for child in ast.iter_child_nodes(node):
                    self.child_to_parent[child] = node

    def run(self):
        visitors = [
            JsonifyVisitor(self.child_to_parent),
            SendFileChecksVisitor(),
            SecureSetCookiesVisitor(),
            UnescapedTemplateFileExtensionsVisitor(),
            AppRouteVisitor(self.filename)
        ]
        for visitor in visitors:
            visitor.visit(self.tree)
            for report in visitor.report_nodes:
                node = report["node"]
                message = report["message"]
                yield (
                    node.lineno,
                    node.col_offset,
                    message,
                    visitor.__class__.__name__,
                )