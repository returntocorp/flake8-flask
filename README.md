# flake8-flask

flake8-flask is a plugin for flake8 with checks specifically for the [flask](https://pypi.org/project/Flask/) framework, written by [r2c](https://r2c.dev)

## Installation

```
pip install flake8-flask
```

Validate the install using `--version`.

```
> flake8 --version
3.7.9 (flake8-flask: 0.1.5, mccabe: 0.6.1, pycodestyle: 2.5.0, pyflakes: 2.1.1)
```

## List of warnings

`r2c-need-filename-or-mimetype-for-file-objects-in-send-file`: This check detects the use of a file-like object in `flask.send_file` without either `mimetype` or `attachment_filename` keyword arguments. `send_file` will throw a ValueError in this situation.

`r2c-secure-set-cookie`: This check detects calls to `response.set_cookie` that do not have `secure`, `httponly`, and `samesite` set. This follows the [guidance in the Flask documentation](https://flask.palletsprojects.com/en/1.1.x/security/#set-cookie-options).

Have an idea for a check? Reach out to us at https://r2c.dev!
