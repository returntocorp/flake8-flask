import ast

import pytest

from flake8_flask.import_aliasing import MethodVisitor


def check_code(code):
    tree = ast.parse(code)
    visitor = MethodVisitor()
    visitor.visit(tree)
    return visitor

def test_import():
    code = """
import flask

app = flask.Flask(__name__)

# True positives
@app.route("/user")
def user():
    user_dict = get_user(request.args.get("id"))
    return json.dumps(user_dict)
"""
    vis = check_code(code)
    assert len(vis.modules) == 1
    assert "flask" in vis.modules


def test_multiple_imports():
    code = """
import flask
import json

app = flask.Flask(__name__)

@app.route("/user2")
def user2():
    from json import dumps

    user_dict = get_user(request.args.get("id"))
    return dumps(user_dict)
"""
    vis = check_code(code)
    assert len(vis.modules) == 2
    assert "flask" in vis.modules
    assert "json" in vis.modules


def test_multiple_imports_single_line():
    code = """
import flask, json

app = flask.Flask(__name__)

@app.route("/user2")
def user2():
    from json import dumps

    user_dict = get_user(request.args.get("id"))
    return dumps(user_dict)
"""
    vis = check_code(code)
    assert len(vis.modules) == 2
    assert "flask" in vis.modules
    assert "json" in vis.modules

def test_is_imported():
    code = """
import flask
import json
import os, sys
"""
    vis = check_code(code)
    assert vis.is_imported("flask") == True
    assert vis.is_imported("json") == True
    assert vis.is_imported("os") == True
    assert vis.is_imported("sys") == True

def test_import_aliasing():
    code = """
import flask as fl
app = fl.Flask(__name__)
"""
    vis = check_code(code)
    assert vis.is_imported("flask")
    assert vis.module_aliases["flask"] == "fl"

def test_method_import():
    code = """
from flask import Flask, jsonify

otherapp = Flask(__name__)

@otherapp.route("/otheruser")
def otheruser():
    user_dict = get_user(request.args.get("id"))
    return jsonify(user_dict)
"""
    vis = check_code(code)
    assert len(vis.modules) == 1
    assert "flask" in vis.modules
    assert len(vis.methods["flask"]) == 2
    assert "Flask" in vis.methods["flask"]
    assert "jsonify" in vis.methods["flask"]


def test_is_method_of():
    code = """
from json import dumps, loads
"""
    vis = check_code(code)
    assert vis.is_method_of("dumps", "json") == True
    assert vis.is_method_of("loads", "json") == True
    assert vis.is_method_of("dump", "json") == False
    assert vis.is_method_of("xxxxx", "flask") == False

def test_vanilla_is_method_alias_of():
    code = """
from json import dumps
"""
    vis = check_code(code)
    assert vis.is_method_alias_of("dumps", "dumps", "json")

def test_not_is_method_alias_of():
    code = """
import json
from bson import dumps
"""
    vis = check_code(code)
    assert not vis.is_method_alias_of("dumps", "dumps", "json")


def test_method_import_alias():
    code = """
from flask import Flask as F, jsonify as j
app = F(__name__)

@app.route("/user")
def user():
    user_dict = get_user(request.args.get("id"))
    json_response = j(user_dict)
    return json_response
"""
    vis = check_code(code)
    assert len(vis.modules) == 1
    assert "flask" in vis.modules
    assert len(vis.methods["flask"]) == 2
    assert "Flask" in vis.methods["flask"]
    assert "jsonify" in vis.methods["flask"]
    assert len(vis.method_aliases["flask"].keys()) == 2
    assert "Flask" in vis.method_aliases["flask"].keys()
    assert "jsonify" in vis.method_aliases["flask"].keys()

    assert vis.is_method_alias_of("F", "Flask", "flask")
    assert vis.is_method_alias_of("j", "jsonify", "flask")

    assert vis.is_method_alias_of("xxxxx", "jsonify", "flask") == False
