# flake8-flask

flake8-flask is a plugin for flake8 with checks specifically for the [flask](https://pypi.org/project/Flask/) framework, written by [r2c](https://r2c.dev)

## Installation

```
pip install flake8-flask
```

Validate the install using `--version`.

```
> flake8 --version
3.7.9 (flake8-flask: 0.2.1, mccabe: 0.6.1, pycodestyle: 2.5.0, pyflakes: 2.1.1)
```

## List of warnings

`r2c-flask-send-file-open`: This check detects the use of a file-like object in `flask.send_file` without either `mimetype` or `attachment_filename` keyword arguments. `send_file` will throw a ValueError in this situation.

`r2c-flask-secure-set-cookie`: This check detects calls to `response.set_cookie` that do not have `secure`, `httponly`, and `samesite` set. This follows the [guidance in the Flask documentation](https://flask.palletsprojects.com/en/1.1.x/security/#set-cookie-options).

`r2c-flask-unescaped-file-extension`: Flask will not autoescape Jinja templates that do not have .html, .htm, .xml, or .xhtml as extensions. This check will alert you if you do not have one of these extensions. This check will also do its best to detect if context variables are escaped if a non-escaped extension is used.

Have an idea for a check? Reach out to us at https://r2c.dev!
