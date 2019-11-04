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

def test_conditional_where_could_be_file_like():
    code = """
import flask
cond = True
if cond:
    f = open("file.txt")
else:
    f = "file.txt"
flask.send_file(f)
"""

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

def test_unknown_function():
    code = """
import flask
flask.send_file("file.txt".replace("txt", "csv"))
"""
    tree = ast.parse(code)
    visitor = SendFileChecksVisitor()
    visitor.visit(tree)
    assert len(visitor.report_nodes) == 0

def test_string_returned_from_some_function():
    code = """
import flask, tempfile
fout, abspath = tempfile.mkstemp()
fout.write("blah")
fout.close()
flask.send_file(abspath)
"""
    tree = ast.parse(code)
    visitor = SendFileChecksVisitor()
    visitor.visit(tree)
    assert len(visitor.report_nodes) == 0

def test_string_returned_from_some_function_inline():
    code = """
import flask
def fxn():
    return open("file.txt", 'rb')
flask.send_file(fxn())
"""
    tree = ast.parse(code)
    visitor = SendFileChecksVisitor()
    visitor.visit(tree)
    assert len(visitor.report_nodes) == 0

def test_format_string():
    # https://github.com/Tethik/faktura/blob/a2ffa7d93d9b4afbaafe02e5ae65c5e3541fd969/faktura/invoice.py#L61
    code = """
import flask
def pdf(invoice_id): 
    pdfdir = app.config["PDF_DIRECTORY"]
    return send_file('{}/{}.pdf'.format(pdfdir, invoice_id))
"""
    tree = ast.parse(code)
    visitor = SendFileChecksVisitor()
    visitor.visit(tree)
    assert len(visitor.report_nodes) == 0

def test_string_bin_op():
    # https://github.com/borevitzlab/spc-eyepi/blob/a5f697c7b7302de088bff0dc834e33604665830b/webinterface.py#L336
    code = """
from flask import send_file
return send_file("static/temp/" + str(serialnumber) + ".jpg")
"""
    tree = ast.parse(code)
    visitor = SendFileChecksVisitor()
    visitor.visit(tree)
    assert len(visitor.report_nodes) == 0

def test_unknown_object():
    # https://github.com/Eierkopp/triparchive/blob/7b5333084ba40263bfcf26aecca6ee8ad4b9c781/triptools/photoserve.py#L140
    code = """
from flask import send_file
def sendimg(id):
    photo = db.get_photo(id)
    return send_file(photo.filename)
"""
    tree = ast.parse(code)
    visitor = SendFileChecksVisitor()
    visitor.visit(tree)
    assert len(visitor.report_nodes) == 0

def test_list_index():
    code = """
from flask import send_file
l = [open("file.txt", 'rb')]
send_file(l[0])
"""
    tree = ast.parse(code)
    visitor = SendFileChecksVisitor()
    visitor.visit(tree)
    assert len(visitor.report_nodes) == 0