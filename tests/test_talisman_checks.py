import ast
from flake8_flask.talisman_checks import TalismanChecks


def check_code(s):
    checker = TalismanChecks(tree=ast.parse(s))
    return list(checker.run())


## SHOULD NOT ALERT
def test_correctly_setup():
    code = """
from flask import Flask
from flask_talisman import Talisman

app = Flask(__name__)
Talisman(app)
"""
    assert check_code(code) == []


def test_correctly_setup_diff_import():
    code = """
from flask import Flask
import flask_talisman

app = Flask(__name__)
flask_talisman.Talisman(app)
"""
    assert check_code(code) == []


def test_basic_app_without_talisman():
    code = """
from flask import Flask; app = Flask(__name__)
"""
    assert check_code(code) == []


## SHOULD ALERT


def test_basic_app_with_talisman_no_init():
    code = """
from flask import Flask
import flask_talisman

app = Flask(__name__)
"""
    assert len(check_code(code)) == 1


# Import but no init
def test_basic_app_with_talisman_no_init():
    code = """
from flask import Flask
from flask_talisman import Talisman

app = Flask(__name__)
"""
    assert len(check_code(code)) == 1
