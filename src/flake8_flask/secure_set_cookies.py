import ast
import logging
import sys

from flake8_flask.constants import MODULE_NAME
from flake8_flask.flask_base_visitor import FlaskBaseVisitor

logger = logging.getLogger(__file__)
logger.setLevel(logging.INFO)
handler = logging.StreamHandler(stream=sys.stderr)
handler.setFormatter(
    logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
)
logger.addHandler(handler)


class SecureSetCookiesVisitor(FlaskBaseVisitor):
    name = "r2c-flask-secure-set-cookie"

    def _is_set_cookie(self, call_node):
        if (
            isinstance(call_node.func, ast.Attribute)
            and call_node.func.attr == "set_cookie"
        ):
            return True
        return False

    def visit_Call(self, call_node):
        # If Flask is imported
        if not self.is_imported(MODULE_NAME):
            logger.debug(
                f"{MODULE_NAME} is not imported, any calls to set_cookie probably aren't flask"
            )
            logger.debug(self.modules)

            return

        # and if set_cookie
        if not self._is_set_cookie(call_node):
            logger.debug("Node is not set_cookie")
            return

        # and if secure, httponly, and samesite are set
        kwargs = set([kw.arg for kw in call_node.keywords])
        intersect = {"secure", "httponly", "samesite"}.intersection(kwargs)
        if len(intersect) == 3:
            logger.debug("All three kwargs are present. This is OK")
            return

        logger.debug(f"Found this node: {ast.dump(call_node)}")
        self.report_nodes.append(
            {
                "node": call_node,
                "message": f"{self.name} Flask cookies should be handled securely by setting secure=True, httponly=True, and samesite='Lax' in set_cookie(...).  If your situation calls for different settings, explicitly disable the setting.  If you want to send the cookie over http, set secure=False.  If you want to let client-side JavaScript read the cookie, set httponly=False.  If you want to attach cookies to requests for external sites, set samesite=None.",
            }
        )
