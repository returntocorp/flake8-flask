import ast
import logging
import sys

from r2c_flake8_requests.requests_base_visitor import RequestsBaseVisitor
from r2c_flake8_requests.constants import REQUESTS_API_HTTP_VERBS, REQUESTS_API_TOP_LEVEL

logger = logging.getLogger(__file__)
logger.setLevel(logging.INFO)
handler = logging.StreamHandler(stream=sys.stderr)
handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
logger.addHandler(handler)

class UseTimeout(object):
    name = "UseTimeout"
    version = "0.0.1"
    code = "R2C702"

    def __init__(self, tree):
        self.tree = tree

    def run(self):
        visitor = UseTimeoutVisitor()
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

class UseTimeoutVisitor(RequestsBaseVisitor):
 
    def visit_Call(self, call_node):
        logger.debug(f"Visiting Call node: {ast.dump(call_node)}")
        if not call_node.func:
            logger.debug("Call node func does not exist")
            return

        fxn_name = self._get_function_name(call_node)
        logger.debug(f"Found function name: {fxn_name}")
        if fxn_name not in set(list(REQUESTS_API_HTTP_VERBS) + list(REQUESTS_API_TOP_LEVEL)):
            logger.debug("Function is not one of the requests API call")
            return
        if not self.is_method(call_node, fxn_name):
            logger.debug("Call node is not a requests API call")
            return

        keywords = call_node.keywords
        if any([kw.arg == "timeout" for kw in keywords]):
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
        tree = ast.parse(fin.read())

    visitor = UseTimeoutVisitor()
    visitor.visit(tree)