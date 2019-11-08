from flask import Flask
import flask_talisman

app = Flask(__name__)
flask_talisman.Talisman(app)


@app.route("/")
def hello():
    return "Hello World!"


if __name__ == "__main__":
    app.run(debug=True)
