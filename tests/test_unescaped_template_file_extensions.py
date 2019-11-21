import ast
import logging

import pytest
from flake8_flask.unescaped_template_file_extensions import (
    UnescapedTemplateFileExtensionsVisitor,
    escaped_extensions,
    logger,
)

logger.setLevel(logging.DEBUG)


def check_code(code):
    tree = ast.parse(code)
    for node in ast.walk(tree):
        for child in ast.iter_child_nodes(node):
            child.parent = node
    visitor = UnescapedTemplateFileExtensionsVisitor()
    visitor.visit(tree)
    return visitor.report_nodes


boilerplate = """
from flask import Flask, render_template
app = Flask(__name__)
"""


@pytest.mark.true_positive
def test_unsafe_extension():
    code = (
        boilerplate
        + """
@app.route("/unsafe")
def unsafe():
    return render_template("unsafe.txt", name=request.args.get("name"))
"""
    )
    assert len(check_code(code)) == 1


@pytest.mark.true_positive
def test_unsafe_extension_with_variables():
    code = (
        boilerplate
        + """
@app.route("/unsafe")
def unsafe():
    name = request.args.get("name")
    age = request.args.get("age")
    return render_template("unsafe.txt", name=name, age=age)
"""
    )
    assert len(check_code(code)) == 1


@pytest.mark.true_positive
def test_no_extension():
    code = (
        boilerplate
        + """
@app.route("/no_extension")
def no_extension():
    return render_template("unsafe", name=request.args.get("name"))
"""
    )
    assert len(check_code(code)) == 1


@pytest.mark.true_positive
def test_a_bunch_of_unescaped_extensions():
    code = (
        boilerplate
        + """
evil = "<script>alert('blah')</script>"
@app.route("/one")
def one():
    return render_template("unsafe.unsafe", name=evil)

@app.route("/two")
def two():
    return render_template("unsafe.email", name=evil)

@app.route("/three")
def three():
    return render_template("unsafe.jinja2", name=evil)

@app.route("/four")
def four():
    return render_template("unsafe.template", name=evil)

@app.route("/five")
def five():
    return render_template("unsafe.asdlfkjasdlkjf", name=evil)
"""
    )
    assert len(check_code(code)) == 5


@pytest.mark.true_positive
def test_some_escaped():
    code = """
import flask
app = flask.Flask(__name__)

@app.route("/escaped_variables")
def escaped_variables():
    name = request.args.get("name")
    age = request.args.get("age")
    return flask.render_template("unsafe.txt", name=flask.Markup.escape(name), age=age)
"""
    assert len(check_code(code)) == 1


@pytest.mark.true_positive
def test_possibly_unsafe_extension():
    code = (
        boilerplate
        + """
@app.route("/what_if")
def what_if():
    cond = request.args.get("cond")
    if cond:
        template = "unsafe.txt"
    else:
        template = "safe.html"
    return render_template(template, cond=cond)
"""
    )
    results = check_code(code)
    assert len(results) == 1
    assert str({"txt"}) in results[0]["message"]


# With edge cases active
@pytest.mark.true_positive
def test_return_with_content_type_text_active():
    code = (
        boilerplate
        + """
@app.route("/opml")
def opml():
    sort_key = flask.request.args.get("sort", "(unread > 0) DESC, snr")
    if sort_key == "feed_title":
        sort_key = "lower(feed_title)"
    order = flask.request.args.get("order", "DESC")
    with dbop.db() as db:
        rows = dbop.opml(db)
        return (
            flask.render_template("opml.opml", atom_content=atom_content, rows=rows),
            200,
            {"Content-Type": "text/plain"},
        )
"""
    )
    tree = ast.parse(code)
    for node in ast.walk(tree):
        for child in ast.iter_child_nodes(node):
            child.parent = node
    visitor = UnescapedTemplateFileExtensionsVisitor(filter_edge_cases=False)
    visitor.visit(tree)
    assert len(visitor.report_nodes) == 1


## True negatives
@pytest.mark.true_negative
def test_no_variables():
    code = (
        boilerplate
        + """
@app.route("no_vars")
def no_vars():
    return render_template("unsafe.txt")
"""
    )
    assert len(check_code(code)) == 0


@pytest.mark.true_negative
def test_escaped_extension():
    code = (
        boilerplate
        + """
@app.route("/escaped_extensions")
def escaped_extensions():
    return render_template("safe.html", name=request.args.get("name"))
"""
    )
    assert len(check_code(code)) == 0


@pytest.mark.true_negative
def test_all_escaped_extensions():
    template = """
@app.route("{}")
def {}():
    return render_template("safe.{}", name=request.args.get("name"))
"""
    code = boilerplate + "\n".join(
        [template.format(ext, ext, ext) for ext in escaped_extensions]
    )
    assert len(check_code(code)) == 0


@pytest.mark.true_negative
def test_escaped_context_variables():
    code = """
import flask
app = flask.Flask(__name__)

@app.route("/escaped_variables")
def escaped_variables():
    name = request.args.get("name")
    return flask.render_template("unsafe.txt", name=flask.Markup.escape(name))
"""
    assert len(check_code(code)) == 0


@pytest.mark.true_negative
def test_all_escaped_context_variables():
    code = """
import flask
app = flask.Flask(__name__)

@app.route("/many_escaped_vars")
def many_escaped_vars():
    var1 = request.args.get("var1")
    var2 = request.args.get("var2")
    var3 = request.args.get("var3")
    return flask.render_template(
        "unsafe.txt",
        var1=flask.Markup.escape(var1),
        var2=flask.Markup.escape(var2),
        var3=flask.Markup.escape(var3)
    )
"""
    assert len(check_code(code)) == 0


@pytest.mark.true_negative
def test_not_flask_render_template():
    code = """
from library import render_template

def not_flask():
    return render_template("hello.txt")
"""
    assert len(check_code(code)) == 0


@pytest.mark.true_negative
def test_return_with_content_type_text():
    code = (
        boilerplate
        + """
@app.route("/opml")
def opml():
    sort_key = flask.request.args.get("sort", "(unread > 0) DESC, snr")
    if sort_key == "feed_title":
        sort_key = "lower(feed_title)"
    order = flask.request.args.get("order", "DESC")
    with dbop.db() as db:
        rows = dbop.opml(db)
        return (
            flask.render_template("opml.opml", atom_content=atom_content, rows=rows),
            200,
            {"Content-Type": "text/plain"},
        )
"""
    )
    tree = ast.parse(code)
    for node in ast.walk(tree):
        for child in ast.iter_child_nodes(node):
            child.parent = node
    visitor = UnescapedTemplateFileExtensionsVisitor(filter_edge_cases=True)
    visitor.visit(tree)
    assert len(visitor.report_nodes) == 0


## False negatives

# It might be safe to assume that sanitization is the
# last thing that happens before it gets rendered, since once
# it's touched again it's no longer considered "sanitized".
# @pytest.mark.false_negative
# def test_flow_through_sanitizer():
#    code = (
#        boilerplate
#        + """
# @app.route("/taint")
# def taint():
#    name = request.args.get("name")
#    safe_name = flask.Markup.escape(name)
#    return render_template("unsafe.txt", name=safe_name)
# """
#    )
#    assert len(check_code(code)) == 0
