## SHOULD ALERT
from flask import send_file as sndfl
sndfl(open("file.txt"))

# flask.send_file case
def example1():
    import flask
    flask.send_file(open("file.txt", 'r'))

# With keyword args
def example2():
    import flask
    flask.send_file(open("file.txt", 'r'), conditional=False)

# from flask import send_file case
def example3():
    from flask import send_file
    send_file(open("file.txt", 'r'))

# Variable resolution
def example4():
    from flask import send_file
    fin = open("file.txt", 'r')
    send_file(fin)

def without_filemode():
    import flask
    fin = open("file.txt")
    flask.send_file(fin)

# Variable resolution with other statements
def example5():
    from flask import send_file
    fin = open("file.txt", 'r')
    print("random statement")
    send_file(fin, conditional=False)

# Import aliasing
def module_alias():
    import flask as fl
    fl.send_file(open("foo.txt"))

def method_alias():
    from flask import send_file as sf
    sf(open("foo.txt"))

## SHOULD NOT ALERT

# Has a mimetype
def example6():
    import flask
    flask.send_file(open("file.txt", 'r'), mimetype="text/plain")

def example7():
    import flask
    flask.send_file(open("file.txt", 'r'), mimetype="text/plain", conditional=False)

# Has a attachment_filename
def example8():
    from flask import send_file
    fin = open("file.txt", 'r')
    send_file(fin, as_attachment=True, attachment_filename="file.txt")

def example9():
    from flask import send_file
    fin = open("file.txt", 'r')
    send_file(fin, as_attachment=True, attachment_filename="file.txt", conditional=False)

# String argument for arg0
def example10():
    import flask
    flask.send_file("/tmp/file.txt")

def example11():
    import flask, os
    flask.send_file(os.path.join("data", "file.txt"))
