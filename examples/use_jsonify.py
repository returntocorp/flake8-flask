import flask

# import jsonify directly
from flask import Flask, jsonify

app = flask.Flask(__name__)

# True positives
@app.route("/user")
def user():
    user_dict = get_user(request.args.get("id"))
    return json.dumps(user_dict)


@app.route("/user2")
def user2():
    from json import dumps

    user_dict = get_user(request.args.get("id"))
    return dumps(user_dict)


# False positives
# Import flask
@app.route("/jsonify_user")
def jsonify_user():
    user_dict = get_user(request.args.get("id"))
    return flask.jsonify(user_dict)


otherapp = Flask(__name__)


@otherapp.route("/otheruser")
def otheruser():
    user_dict = get_user(request.args.get("id"))
    return jsonify(user_dict)
