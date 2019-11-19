from flake8_flask.secure_set_cookies import SecureSetCookiesVisitor
from flake8_flask.send_file_checks import SendFileChecksVisitor


class Flake8Flask:
    name = "flake8-flask"
    version = "0.1.4"

    def __init__(self, tree):
        self.tree = tree

    def run(self):
        visitors = [SendFileChecksVisitor(), SecureSetCookiesVisitor()]
        for visitor in visitors:
            visitor.visit(self.tree)

            for report in visitor.report_nodes:
                node = report["node"]
                message = report["message"]
                yield (node.lineno, node.col_offset, message, visitor.__class__.__name__)
