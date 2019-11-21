from flask import Flask, render_template

app = Flask(__name__)

# True positives
@app.route("/unsafe")
def unsafe():
    return render_template("unsafe.txt", name=request.args.get("name"))


@app.route("/unsafe2")
def unsafe2():
    name = request.args.get("name")
    return render_template("unsafe.txt", name=name)


@app.route("/also_unsafe")
def also_unsafe():
    template = "page.unsafe"
    return render_template(template, value=request.args.get("value"))


# True negatives
@app.route("/safe_extension")
def safe_extension():
    return render_template("safe.html", name=request.args.get("name"))


@app.route("/escaped_variables")
def escaped_variables():
    name = request.args.get("name")
    return render_template("unsafe.txt", name=flask.Markup.escape(name))


# False negatives
@app.route("/taint")
def taint():
    name = request.args.get("name")
    safe_name = flask.Markup.escape(name)
    return render_template("unsafe.txt", name=safe_name)
