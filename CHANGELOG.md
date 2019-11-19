# 0.1.5

- moved all the Visitor classes to a single entrypoint. This keeps the plugin from looking like individually installed plugins for each check.

# 0.1.4

- fixed a bug in import resolution that missed `from flask_talisman import Talisman`

# 0.1.3

- Introduced R2C204 - Talisman for testing. This check will fire when flask-talisman (https://github.com/GoogleCloudPlatform/flask-talisman) is not used.

# 0.1.2

- added content-type to setup.py

# 0.1.1

- added a better README
- added README to setup.py

# 0.1.0

- release to pypi (https://pypi.org/project/flake8-flask/)

# 0.0.9

- bugfixes for set_cookie check
- set_cookie will now check to see if flask is imported in the same file. This reduces false positives with other set_cookie methods in modules like `cookiejar`

# 0.0.8

- added false negative test cases send_file for `with open(...)` and `String.IO` cases
- added `true_positive`, `true_negative`, and `false_negative` pytest markers for more clarity. `false_negatives` exist for future improvements
- added a new check to detect secure keyword arguments being set in `set_cookie` method of Flask's Response object. This check will alert when `secure`, `httponly`, and `samesite` are not present in a call to `set_cookie`.

# 0.0.7

- no significant changes, just making automated version detections happy

# 0.0.6

- fixed an issue where the check would fire on any AST node type that was not explicitly checked for

# 0.0.5

- send_file check now supports format strings
- updated check to only fire if the first argument can be resolved to the open('filename', ...) pattern, reducing false positives.

# 0.0.4

- fixed a problem with the flake8 entrypoint. Will now run as a flake8 plugin properly

# 0.0.3

- fixed a problem with import aliasing not resolving correctly to send_file or flask.send_file

# 0.0.2

- send_file check supports variable resolution
- fixed some copy-pasta text that was preventing correct operation
- added tests and examples for this check

# 0.0.1

Include check for flask.send_file. This check prevents a ValueError from being raised when a file-like object is passed to `flask.send_file` without either `mimetype` or `attachment_filename` keyword arguments set.
