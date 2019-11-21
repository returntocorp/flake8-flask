import ast

import pytest
from flake8_flask.secure_set_cookies import SecureSetCookiesVisitor


# secure is not set, httponly is not set, samesite is not set
@pytest.mark.true_positive
def test_no_secure_kwargs_set():
    code = """
import flask
response = flask.make_response()
response.set_cookie("cookie_name", "cookie_value")
"""
    tree = ast.parse(code)
    visitor = SecureSetCookiesVisitor()
    visitor.visit(tree)
    assert len(visitor.report_nodes) == 1


@pytest.mark.true_positive
def test_some_secure_kwargs_set():
    code = """
from flask import make_response
r = make_response()
# some values are set but not others
r.set_cookie("cookie1", "cookie_value", secure=True)
r.set_cookie("cookie2", "cookie_value", httponly=True)
r.set_cookie("cookie3", "cookie_value", samesite="Lax")
r.set_cookie("cookie4", "cookie_value", secure=True, httponly=True)
r.set_cookie("cookie5", "cookie_value", httponly=True, samesite="Lax")
"""
    tree = ast.parse(code)
    visitor = SecureSetCookiesVisitor()
    visitor.visit(tree)
    assert len(visitor.report_nodes) == 5


@pytest.mark.true_positive
def test_kwargs_present_but_disabled():
    code = """
from flask import make_response
r = make_response()
# explicitly disabled
r.set_cookie("cookie6", "cookie_value", secure=False)
r.set_cookie("cookie7", "cookie_value", httponly=False)
r.set_cookie("cookie8", "cookie_value", samesite=None)
r.set_cookie("cookie9", "cookie_value", secure=False, httponly=False)
r.set_cookie("cookie10", "cookie_value", httponly=False, samesite=None)
"""
    tree = ast.parse(code)
    visitor = SecureSetCookiesVisitor()
    visitor.visit(tree)
    assert len(visitor.report_nodes) == 5


@pytest.mark.true_negative
def test_all_secure_kwargs_set():
    code = """
# All kwargs present
def all_set():
    import flask
    response = flask.make_response()
    response.set_cookie("cookie1", "cookie_value", secure=True, httponly=True, samesite='Lax')
    response.set_cookie("cookie2", "cookie_value", secure=True, httponly=True, samesite='Strict')
    response.set_cookie("cookie3", "cookie_value", secure=False, httponly=False, samesite=None)
"""
    tree = ast.parse(code)
    visitor = SecureSetCookiesVisitor()
    visitor.visit(tree)
    assert len(visitor.report_nodes) == 0


@pytest.mark.true_negative
def test_loose_set_cookie():
    code = """
def loose_set_cookie():
    set_cookie("this isn't actually a flask response, since set_cookie is a Response method")
"""
    tree = ast.parse(code)
    visitor = SecureSetCookiesVisitor()
    visitor.visit(tree)
    assert len(visitor.report_nodes) == 0


# homebrew set_cookie
@pytest.mark.true_negative
def test_homebrew_set_cookie():
    code = """
def set_cookie(settings):
    d = {"hello": "world"}
    d.update(settings)
    return d

def use_cookie(cookie):
    foo = set_cookie({"goodbye": "planet"})
"""
    tree = ast.parse(code)
    visitor = SecureSetCookiesVisitor()
    visitor.visit(tree)
    assert len(visitor.report_nodes) == 0


# non-Flask set-cookie
@pytest.mark.true_negative
def test_non_flask_set_cookie():
    # https://github.com/cruzegoodin/TSC-ShippingDetails/blob/cceee79014623c5ac8fb042b8301a427743627d6/venv/lib/python2.7/site-packages/pip/_vendor/requests/cookies.py#L306
    code = """
import copy
import time
import collections
from .compat import cookielib, urlparse, urlunparse, Morsel

def merge_cookies(cookiejar, cookies):
    if not isinstance(cookiejar, cookielib.CookieJar):
        raise ValueError('You can only merge into CookieJar')

    if isinstance(cookies, dict):
        cookiejar = cookiejar_from_dict(
            cookies, cookiejar=cookiejar, overwrite=False)
    elif isinstance(cookies, cookielib.CookieJar):
        try:
            cookiejar.update(cookies)
        except AttributeError:
            for cookie_in_jar in cookies:
                cookiejar.set_cookie(cookie_in_jar)

    return cookiejar
"""
    tree = ast.parse(code)
    visitor = SecureSetCookiesVisitor()
    visitor.visit(tree)
    assert len(visitor.report_nodes) == 0
