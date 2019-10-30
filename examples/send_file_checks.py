## SHOULD ALERT
# flask.send_file case
import flask
flask.send_file(open("file.txt", 'r'))

# With keyword args
import flask
flask.send_file(open("file.txt", 'r'), conditional=False)

# from flask import send_file case
from flask import send_file
send_file(open("file.txt", 'r'))

# Variable resolution
from flask import send_file
fin = open("file.txt", 'r')
send_file(fin)

# Variable resolution with other statements
from flask import send_file
fin = open("file.txt", 'r')
print("random statement")
send_file(fin, conditional=False)

## SHOULD NOT ALERT
# Has a mime_type
import flask
flask.send_file(open("file.txt", 'r'), mime_type="text/plain")

import flask
flask.send_file(open("file.txt", 'r'), mime_type="text/plain", conditional=False)

# Has a attachment_filename
from flask import send_file
fin = open("file.txt", 'r')
send_file(fin, as_attachment=True, attachment_filename="file.txt")

from flask import send_file
fin = open("file.txt", 'r')
send_file(fin, as_attachment=True, attachment_filename="file.txt", conditional=False)

# String argument for arg0
import flask
flask.send_file("/tmp/file.txt")

import flask
flask.send_file(os.path.join("data", "file.txt"))
