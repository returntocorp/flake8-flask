import ast
import pytest

from flake8_flask.upsell_blueprint import AppRouteVisitor

def check_code(code):
    tree = ast.parse(code)
    for node in ast.walk(tree):
        for child in ast.iter_child_nodes(node):
            child.parent = node
    visitor = AppRouteVisitor()
    visitor.visit(tree)
    return visitor.report_nodes

boilerplate = """
from flask import Flask
app = Flask(__name__)
"""
@pytest.mark.true_positive
def test_app_routes_complex():
    code = (
        boilerplate
        + """
@app.route("/")
def complex():
    print(a)
    print(a)
    print(a)
    print(a)
    print(a)
    print(a)
    print(a)
    print(a)
    print(a)
    return render_template()
"""
    )
    assert len(check_code(code)) == 1
@pytest.mark.true_positive
def test_app_aliasing():
    code = """
from flask import Flask
my_flask_app = Flask(__name__)
@my_flask_app.route("/unsafe")
def unsafe():
    print(a)
    print(a)
    print(a)
    print(a)
    print(a)
    print(a)
    print(a)
    print(a)
    print(a)
    print(a)
    return render_template("unsafe.txt", name=request.args.get("name"))
"""

@pytest.mark.true_negative
def test_app_routes_simple():
    code = (
        boilerplate
        + """
@app.route("/")
def complex():
    return jsonify()
"""
    )
    assert len(check_code(code)) == 0

@pytest.mark.true_negative
def test_other_route_decorators():
    code = (
        boilerplate
        + """
@newmodule.route("/")
def complex():
    print(a)
    print(a)
    print(a)
    print(a)
    print(a)
    print(a)
    print(a)
    print(a)
    print(a)
    return jsonify()
"""
    )
    assert len(check_code(code)) == 0