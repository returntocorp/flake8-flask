import ast
import logging
import sys
from flake8_flask.flask_base_visitor import FlaskBaseVisitor

logger = logging.getLogger(__file__)
logger.setLevel(logging.INFO)
handler = logging.StreamHandler(stream=sys.stderr)
handler.setFormatter(logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s"))
logger.addHandler(handler)


class SecureSetCookies:
    name = "SecureSetCookies"
    version = "0.0.1"
    code = "R2C203"

    def __init__(self, tree):
        self.tree = tree

    def run(self):
        visitor = SecureSetCookiesVisitor()
        visitor.visit(tree)

        for report in visitor.report_nodes:
            node = report["node"]
            yield (
                node.lineno,
                node.col_offset,
                self._message_for(),
                self.name,
            )

    def _message_for(self):
        return f"{self.code} Cookies should be handled securely by setting secure=True, httponly=True, and samesite='Lax'.  If your situation calls for different settings, explicitly disable the setting.  If you want to send the cookie over http, set secure=False.  If you want to let client-side JavaScript read the cookie, set httponly=False.  If you want to attach cookies to requests for external sites, set samesite=None."


class SecureSetCookiesVisitor(FlaskBaseVisitor):
    def _is_set_cookie(self, call_node):
        if isinstance(call_node.func, ast.Attribute) and call_node.func.attr == "set_cookie":
            return True
        return False

    def visit_Call(self, call_node):
        # If Flask is imported

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
            {"node": call_node,}
        )


if __name__ == "__main__":
    import argparse

    logger.setLevel(logging.DEBUG)

    parser = argparse.ArgumentParser()
    # Add arguments here
    parser.add_argument("inputfile")

    args = parser.parse_args()

    logger.info(f"Parsing {args.inputfile}")
    with open(args.inputfile, "r") as fin:
        data = fin.read()
    tree = ast.parse(data)
    lines = data.split("\n")

    visitor = SecureSetCookiesVisitor()
    visitor.visit(tree)
    print("*** Hits:")
    for report in visitor.report_nodes:
        node = report["node"]
        print(node.lineno, node.col_offset, lines[node.lineno - 1])

