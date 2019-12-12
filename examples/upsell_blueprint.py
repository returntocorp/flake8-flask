from flask import Flask

app = Flask(__name__)

@app.route("/user")
def user():
    return
@app.route("/user/a")
def user_a():
    return

@app.route("/user/b")
def user_b():
    return

if __name__ == "__main__":
    app.run(debug=True)
