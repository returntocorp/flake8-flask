import ast
import logging
import sys

from flake8_flask.flask_base_visitor import FlaskBaseVisitor

logger = logging.getLogger(__file__)
logger.setLevel(logging.INFO)
handler = logging.StreamHandler(stream=sys.stderr)
handler.setFormatter(
    logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
)
logger.addHandler(handler)

MODULE_NAME = "flask_talisman"
FLASK_NAME = "flask"

FUNCTION_NAME = "Talisman"
FLASK_FUNCTION_NAME = "Flask"


class TalismanChecks(object):
    name = "TalismanChecks"
    version = "0.0.1"
    code = "R2C203"

    def __init__(self, tree):
        self.tree = tree

    def run(self):
        self.visitor = TalismanChecksVisitor()
        self.visitor.visit(self.tree)

        reports = []
        if self.visitor._flask_initialized and not self.visitor._talimans_initialized:
            reports = self.visitor.report_nodes

        for report in reports:
            node = report["node"]
            yield (node.lineno, node.col_offset, self._message_for(node), self.name)

    def _message_for(self, node):
        if self.visitor._talisman_imported:
            return f"{self.code} good job using flask_talisman but it's not initialized"
        else:
            return (
                f"{self.code} you should use flask_talisman to properly secure your app"
            )


class TalismanChecksVisitor(FlaskBaseVisitor):
    def __init__(self):
        self._talisman_imported = False
        self._flask_imported = False
        self._talimans_initialized = False
        self._flask_initialized = False
        super(TalismanChecksVisitor, self).__init__()

    def visit_Import(self, import_node):
        logger.debug(f"Visiting Import node: {ast.dump(import_node)}")
        # TODO detect import
        names = {alias.name for alias in import_node.names}
        if MODULE_NAME in names:
            self._talisman_imported = True
        elif FLASK_NAME in names:
            self._flask_imported = True

    def visit_ImportFrom(self, import_from_node):
        logger.debug(f"Visiting ImportFrom node: {ast.dump(import_from_node)}")
        if import_from_node.module == MODULE_NAME:
            self._talisman_imported = True
        elif import_from_node.module == FLASK_NAME:
            self._flask_imported = True

    def visit_Call(self, call_node):
        logger.debug(f"Visiting Call node: {ast.dump(call_node)}")
        if not call_node.func:
            logger.debug("Call node func does not exist")
            return

        fxn_name = self._get_function_name(call_node)
        logger.debug(f"Found function name: {fxn_name}")
        # TODO do the logic here

        if fxn_name == FLASK_FUNCTION_NAME:
            self._flask_initialized = True
            logger.debug(f"Found this node: {ast.dump(call_node)}")
            self.report_nodes.append({"node": call_node})
        elif fxn_name == FUNCTION_NAME:
            self._talimans_initialized = True


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

    visitor = TalismanChecksVisitor()
    visitor.visit(tree)
    print("*** Hits:")
    for report in visitor.report_nodes:
        node = report["node"]
        print(node.lineno, node.col_offset, lines[node.lineno - 1])
