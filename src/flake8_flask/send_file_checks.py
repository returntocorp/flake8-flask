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


class SendFileChecks(object):
    name = "need-filename-or-mimetype-for-file-objects-in-send-file"
    version = "0.0.7"
    code = "R2C202"

    def __init__(self, tree):
        self.tree = tree

    def run(self):
        visitor = SendFileChecksVisitor()
        visitor.visit(self.tree)

        for report in visitor.report_nodes:
            node = report["node"]
            yield (
                node.lineno,
                node.col_offset,
                self._message_for(),
                self.name,
            )

    def _message_for(self):
        return f"{self.code} passing a file-like object to flask.send_file without a mimetype or attachment_filename will raise a ValueError"


class SendFileChecksVisitor(FlaskBaseVisitor):
    def _is_os_path_join(self, call_node):
        # This makes me sad but it'll work.
        if (
            isinstance(call_node.func, ast.Attribute)
            and isinstance(call_node.func.value, ast.Attribute)
            and isinstance(call_node.func.value.value, ast.Name)
        ):
            return (
                call_node.func.value.value.id == "os"
                and call_node.func.value.attr == "path"
                and call_node.func.attr == "join"
            )

    def _is_format_string(self, call_node):
        if isinstance(call_node.func, ast.Attribute):
            if call_node.func.attr == "format" and isinstance(
                call_node.func.value, ast.Str
            ):
                return True
        return False

    def _is_open(self, node):
        if isinstance(node, ast.Call):
            if isinstance(node.func, ast.Name) and node.func.id == "open":
                return True
        return False

    def _is_name_node_open(self, name_node):
        variable_assigment_nodes = self.get_symbol_value_nodes(name_node.id)
        return any([self._is_open(node) for node in variable_assigment_nodes])

    def visit_Call(self, call_node):
        logger.debug(f"Visiting Call node: {ast.dump(call_node)}")
        if not call_node.func:
            logger.debug("Call node func does not exist")
            return

        fxn_name = self._get_function_name(call_node)
        logger.debug(f"Found function name: {fxn_name}")
        if not self.is_method(call_node, "send_file"):
            logger.debug("Call node is not a flask API call")
            return

        arg0 = call_node.args[0]
        if isinstance(arg0, ast.Str):
            logger.debug("Call to send_file is a string, so s'all good man.")
            return
        elif isinstance(arg0, ast.Name):
            if not self._is_name_node_open(arg0):
                logger.debug(
                    "Variable dosn't resolve to open(...), so assuming we're good"
                )
                return
        elif isinstance(arg0, ast.Call):
            if not self._is_open(arg0):
                logger.debug("arg0 is not open(...), so don't care")
                return
        else:
            # This means arg0 is some other node type besides Call or Name, which isn't supported yet.
            logger.debug("arg0 is not Call or Name node, so we're bailing out.")
            return

        keywords = call_node.keywords
        if any([kw.arg == "mimetype" for kw in keywords]):
            logger.debug("requests call has the 'timeout' keyword, so we're good")
            return
        if any([kw.arg == "attachment_filename" for kw in keywords]):
            logger.debug("requests call has the 'timeout' keyword, so we're good")
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

    visitor = SendFileChecksVisitor()
    visitor.visit(tree)
    print("*** Hits:")
    for report in visitor.report_nodes:
        node = report["node"]
        print(node.lineno, node.col_offset, lines[node.lineno - 1])
