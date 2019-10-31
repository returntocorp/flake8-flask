import ast
import logging
import sys

from flake8_flask.flask_base_visitor import FlaskBaseVisitor

logger = logging.getLogger(__file__)
logger.setLevel(logging.INFO)
handler = logging.StreamHandler(stream=sys.stderr)
handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
logger.addHandler(handler)

class SendFileChecks(object):
    name = "UseTimeout"
    version = "0.0.1"
    code = "R2C202"

    def __init__(self, tree):
        self.tree = tree

    def run(self):
        visitor = FlaskBaseVisitor()
        visitor.visit(self.tree)

        for report in visitor.report_nodes:
            node = report['node']
            yield (
                node.lineno,
                node.col_offset,
                self._message_for(),
                self.name,
            )

    def _message_for(self):
        return f"{self.code} use a timeout; requests will hang forever without a timeout (recommended 60 sec)"

class SendFileChecksVisitor(FlaskBaseVisitor):
 
    def visit_Call(self, call_node):
        logger.debug(f"Visiting Call node: {ast.dump(call_node)}")
        if not call_node.func:
            logger.debug("Call node func does not exist")
            return

        fxn_name = self._get_function_name(call_node)
        logger.debug(f"Found function name: {fxn_name}")
        if not self.is_method(call_node, fxn_name):
            logger.debug("Call node is not a flask API call")
            return

        arg0 = call_node.args[0]
        if isinstance(arg0, ast.Str):
            logger.debug("Call to send_file is a string, so s'all good man.")
            return

        keywords = call_node.keywords
        if any([kw.arg == "mimetype" for kw in keywords]):
            logger.debug("requests call has the 'timeout' keyword, so we're good")
            return
        if any([kw.arg == "attachment_filename" for kw in keywords]):
            logger.debug("requests call has the 'timeout' keyword, so we're good")
            return

        logger.debug(f"Found this node: {ast.dump(call_node)}")
        self.report_nodes.append({
            "node": call_node,
        })

if __name__ == "__main__":
    import argparse

    logger.setLevel(logging.DEBUG)

    parser = argparse.ArgumentParser()
    # Add arguments here
    parser.add_argument("inputfile")

    args = parser.parse_args()

    logger.info(f"Parsing {args.inputfile}")
    with open(args.inputfile, 'r') as fin:
        data = fin.read()
    tree = ast.parse(data)
    lines = data.split('\n')

    visitor = SendFileChecksVisitor()
    visitor.visit(tree)
    print("*** Hits:")
    for report in visitor.report_nodes:
        node = report['node']
        print(
            node.lineno,
            node.col_offset,
            lines[node.lineno-1]
        )