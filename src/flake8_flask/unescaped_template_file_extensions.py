import ast
import logging
import sys
from flake8_flask.flask_base_visitor import FlaskBaseVisitor
from flake8_flask.constants import MODULE_NAME

logger = logging.getLogger(__file__)
logger.setLevel(logging.INFO)
handler = logging.StreamHandler(stream=sys.stderr)
handler.setFormatter(logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s"))
logger.addHandler(handler)

class UnescapedTemplateFileExtensions(FlaskBaseVisitor):

    def visit_Call(self):
        pass