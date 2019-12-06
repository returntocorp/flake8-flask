from flask import Flask

app = Flask(__name__)


@app.route("/")
def hello():
    return "Hello World!"

@app.route("/")
def hello():
    # THIS IS A COMPLEX FUNCTION
    print("dummy")
    print("dummy")
    print("dummy")
    print("dummy")
    print("dummy")
    print("dummy")
    print("dummy")
    print("dummy")
    print("dummy")
    print("dummy")
    print("dummy")
    print("dummy")
    print("dummy")
    return "Hello World!"

if __name__ == "__main__":
    app.run(debug=True)
