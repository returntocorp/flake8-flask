import ast

import pytest

from flake8_flask.use_jsonify import JsonifyVisitor


def check_code(code):
    tree = ast.parse(code)
    for node in ast.walk(tree):
        for child in ast.iter_child_nodes(node):
            child.parent = node
    visitor = JsonifyVisitor()
    visitor.visit(tree)
    return visitor.report_nodes


@pytest.mark.true_positive
def test_return_json_dumps():
    code = """
import flask

app = flask.Flask(__name__)

# True positives
@app.route("/user")
def user():
    user_dict = get_user(request.args.get("id"))
    return json.dumps(user_dict)
"""
    assert len(check_code(code)) == 1


@pytest.mark.true_positive
def test_return_dumps():
    code = """
import flask

app = flask.Flask(__name__)

@app.route("/user2")
def user2():
    from json import dumps

    user_dict = get_user(request.args.get("id"))
    return dumps(user_dict)
"""
    assert len(check_code(code)) == 1


@pytest.mark.true_negative
def test_return_flask_jsonify():
    code = """
@app.route("/jsonify_user")
def jsonify_user():
    user_dict = get_user(request.args.get("id"))
    return flask.jsonify(user_dict)
"""
    assert len(check_code(code)) == 0


@pytest.mark.true_negative
def test_return_jsonify():
    code = """
from flask import Flask, jsonify

otherapp = Flask(__name__)

@otherapp.route("/otheruser")
def otheruser():
    user_dict = get_user(request.args.get("id"))
    return jsonify(user_dict)
"""
    assert len(check_code(code)) == 0


@pytest.mark.false_negative
def test_variable_resolution():
    code = """
from flask import Flask, jsonify
app = Flask(__name__)

@app.route("/user")
def user():
    user_dict = get_user(request.args.get("id"))
    json_response = jsonify(user_dict)
    return json_response
"""
    assert len(check_code(code)) == 1
