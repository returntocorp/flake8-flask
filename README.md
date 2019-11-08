# flake8-flask

flake8-flask is a plugin for flake8 with checks specifically for the [flask](https://pypi.org/project/Flask/) framework.

## Installation

```
pip install flake8-flask
```

Validate the install using `--version`. flake8-flask adds two plugins, but this will be consolidated in a very near-future version. :)

```
> flake8 --version
3.7.9 (mccabe: 0.6.1, need-filename-or-mimetype-for-file-objects-in-send-file: 0.0.7, pycodestyle: 2.5.0, pyflakes: 2.1.1, secure-set-cookie: 0.0.2)
```

## List of warnings

**R2C202**: `need-filename-or-mimetype-for-file-objects-in-send-file`: This check detects the use of a file-like object in `flask.send_file` without either `mimetype` or `attachment_filename` keyword arguments. `send_file` will throw a ValueError in this situation.

**R2C203**: `secure-set-cookie`: This check detects calls to `response.set_cookie` that do not have `secure`, `httponly`, and `samesite` set. This follows the [guidance in the Flask documentation](https://flask.palletsprojects.com/en/1.1.x/security/#set-cookie-options).


