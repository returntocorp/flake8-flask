import ast
import logging
import sys

from flake8_flask import __version__
from flake8_flask.secure_set_cookies import SecureSetCookiesVisitor
from flake8_flask.send_file_checks import SendFileChecksVisitor

logger = logging.getLogger(__file__)
logger.setLevel(logging.INFO)
handler = logging.StreamHandler(stream=sys.stderr)
handler.setFormatter(logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s"))
logger.addHandler(handler)


class Flake8Flask:
    name = "flake8-flask"
    version = __version__

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

    flake8flask = Flake8Flask(tree)

    print("*** Hits:")
    results = flake8flask.run()
    for report in results:
        print(report)
