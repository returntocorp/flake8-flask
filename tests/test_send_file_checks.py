import ast
from flake8_flask.send_file_checks import SendFileChecksVisitor

## SHOULD ALERT
# flask.send_file case
def test_basic():
    code = """
import flask
flask.send_file(open("file.txt", 'r'))
"""
    tree = ast.parse(code)
    visitor = SendFileChecksVisitor()
    visitor.visit(tree)
    assert len(visitor.report_nodes) == 1

# With keyword args
def test_with_kwargs():
    code = """
import flask
flask.send_file(open("file.txt", 'r'), conditional=False)
"""
    tree = ast.parse(code)
    visitor = SendFileChecksVisitor()
    visitor.visit(tree)
    assert len(visitor.report_nodes) == 1

# from flask import send_file case
def test_import_from():
    code = """
from flask import send_file
send_file(open("file.txt", 'r'))
"""
    tree = ast.parse(code)
    visitor = SendFileChecksVisitor()
    visitor.visit(tree)
    assert len(visitor.report_nodes) == 1

# Variable resolution
def test_variable_resolution():
    code = """
from flask import send_file
fin = open("file.txt", 'r')
send_file(fin)
"""
    tree = ast.parse(code)
    visitor = SendFileChecksVisitor()
    visitor.visit(tree)
    assert len(visitor.report_nodes) == 1

# Variable resolution with other statements
def test_variable_resolution_with_statements():
    code = """
from flask import send_file
fin = open("file.txt", 'r')
print("random statement")
send_file(fin, conditional=False)
"""
    tree = ast.parse(code)
    visitor = SendFileChecksVisitor()
    visitor.visit(tree)
    assert len(visitor.report_nodes) == 1

# Import aliasing
def test_import_aliasing():
    code = """
import flask as fl
fin = open("file.txt", 'r')
fl.send_file(fin)
"""
    tree = ast.parse(code)
    visitor = SendFileChecksVisitor()
    visitor.visit(tree)
    assert len(visitor.report_nodes) == 1

def test_function_import_aliasing():
    code = """
from flask import send_file as sf
fin = open("file.txt", 'r')
sf(fin)
"""
    tree = ast.parse(code)
    visitor = SendFileChecksVisitor()
    visitor.visit(tree)
    assert len(visitor.report_nodes) == 1


## SHOULD NOT ALERT
# Has a mimetype
def test_mimetype_kwarg():
    code = """
import flask
flask.send_file(open("file.txt", 'r'), mimetype="text/plain")
"""
    tree = ast.parse(code)
    visitor = SendFileChecksVisitor()
    visitor.visit(tree)
    assert len(visitor.report_nodes) == 0

def test_mimetype_kwarg_with_others():
    code = """
import flask
flask.send_file(open("file.txt", 'r'), mimetype="text/plain", conditional=False)
"""
    tree = ast.parse(code)
    visitor = SendFileChecksVisitor()
    visitor.visit(tree)
    assert len(visitor.report_nodes) == 0

# Has a attachment_filename
def test_attachment_filename_kwarg():
    code = """
from flask import send_file
fin = open("file.txt", 'r')
send_file(fin, as_attachment=True, attachment_filename="file.txt")
"""
    tree = ast.parse(code)
    visitor = SendFileChecksVisitor()
    visitor.visit(tree)
    assert len(visitor.report_nodes) == 0

def test_attachment_filename_kwarg_with_others():
    code = """
from flask import send_file
fin = open("file.txt", 'r')
send_file(fin, as_attachment=True, attachment_filename="file.txt", conditional=False)
"""
    tree = ast.parse(code)
    visitor = SendFileChecksVisitor()
    visitor.visit(tree)
    assert len(visitor.report_nodes) == 0

# String argument for arg0
def test_string_literal():
    code = """
import flask
flask.send_file("/tmp/file.txt")
"""
    tree = ast.parse(code)
    visitor = SendFileChecksVisitor()
    visitor.visit(tree)
    assert len(visitor.report_nodes) == 0

def test_string_variable_resolution():
    code = """
from flask import send_file
filename = "/tmp/file.txt"
send_file(filename)
"""
    tree = ast.parse(code)
    visitor = SendFileChecksVisitor()
    visitor.visit(tree)
    assert len(visitor.report_nodes) == 0

def test_branch_string_variable_resolution():
    code = """
from flask import send_file
cond = True
if cond:
    filename = "/tmp/file.txt"
else:
    filename = "file.txt"
send_file(filename)
"""
    tree = ast.parse(code)
    visitor = SendFileChecksVisitor()
    visitor.visit(tree)
    assert len(visitor.report_nodes) == 0

def test_os_path_join():
    code = """
import flask, os
flask.send_file(os.path.join("data", "file.txt"))
"""
    tree = ast.parse(code)
    visitor = SendFileChecksVisitor()
    visitor.visit(tree)
    assert len(visitor.report_nodes) == 0