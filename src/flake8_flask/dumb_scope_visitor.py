import ast
import logging
import sys
from collections import defaultdict

from flake8_flask.import_aliasing import MethodVisitor

logger = logging.getLogger(__file__)
logger.setLevel(logging.INFO)
handler = logging.StreamHandler(stream=sys.stderr)
handler.setFormatter(
    logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
)
logger.addHandler(handler)


class DumbScopeVisitor(MethodVisitor):
    def __init__(self):
        self.report_nodes = []
        self.symbol_table = {}
        self._set_scope("global")
        super(DumbScopeVisitor, self).__init__()

    def _symbol_lookup(self, symbol):
        logger.debug(f"Symbol table: {self.symbol_table}")

        try:
            val = self.symbol_table[self.scope][symbol]
        except KeyError:
            logger.debug(
                f"{symbol} not in scope[{self.scope}] symbol table. Case not handled yet"
            )
            return None

        if isinstance(val, ast.Name):
            val = self._symbol_lookup(val.id)
        return val

    def _get_symbol_value(self, value):
        if isinstance(value, ast.Str) or isinstance(value, ast.Bytes):
            return value.s
        elif isinstance(value, ast.Num):
            return value.n
        else:  # TODO handle more cases
            return None

    def _get_possible_symbol_values(self, symbol):
        return [
            self._get_symbol_value(sym) for sym in self.symbol_table[self.scope][symbol]
        ]

    def _symbol_could_be_value(self, symbol, value):
        return any(
            [
                self._get_symbol_value(sym) == value
                for sym in self.symbol_table[self.scope][symbol]
            ]
        )

    def _set_symbol(self, symbol, value_node):
        self.symbol_table[self.scope][symbol].append(value_node)

    def get_symbol_value_nodes(self, symbol):
        return self.symbol_table[self.scope][symbol]

    def _set_scope(self, scope):
        self.scope = scope
        self.symbol_table[self.scope] = defaultdict(list)

    def visit_FunctionDef(self, def_node):
        logger.debug("Visiting FunctionDef node")
        self._set_scope(def_node.name)
        for node in def_node.body:
            self.visit(node)

    def visit_AsyncFunctionDef(self, def_node):
        self.visit_FunctionDef(def_node)

    def visit_ClassDef(self, class_node):
        self._set_scope(class_node.name)
        for node in class_node.body:
            self.visit(node)

    def visit_Assign(self, assign_node):
        logger.debug(f"Visiting Assign node: {ast.dump(assign_node)}")
        target = assign_node.targets[0]
        if isinstance(target, ast.Name):
            if isinstance(target.ctx, ast.Store):
                self._set_symbol(target.id, assign_node.value)
        elif isinstance(target, ast.Tuple):
            if isinstance(target.ctx, ast.Store):
                for i, elem in enumerate(target.elts):
                    if not isinstance(elem, ast.Name):
                        continue  # TODO: need to figure out alternative cases
                    if isinstance(assign_node.value, ast.Tuple):
                        self._set_symbol(elem.id, assign_node.value.elts[i])

        self.visit(assign_node.value)


if __name__ == "__main__":
    import argparse

    logger.setLevel(logging.DEBUG)

    parser = argparse.ArgumentParser()
    # Add arguments here
    parser.add_argument("inputfile")

    args = parser.parse_args()

    logger.info(f"Parsing {args.inputfile}")
    with open(args.inputfile, "r") as fin:
        tree = ast.parse(fin.read())

    visitor = DumbScopeVisitor()
    visitor.visit(tree)
