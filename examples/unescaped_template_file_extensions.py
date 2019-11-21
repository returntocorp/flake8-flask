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


@app.route("/noqa")
def noqa():
    # Forgive the weirdness. It's to get it under black's line length
    # so it doesn't autoformat the noqa onto a different line.
    rt = render_template
    s = "I'll never change"
    t = rt("unsafe.noqa", x=s)  # noqa r2c-unescaped-template-file-extension


# Example of an edge case
@app.route("/opml")
def opml():
    sort_key = flask.request.args.get("sort", "(unread > 0) DESC, snr")
    if sort_key == "feed_title":
        sort_key = "lower(feed_title)"
    order = flask.request.args.get("order", "DESC")
    with dbop.db() as db:
        rows = dbop.opml(db)
        return (
            flask.render_template("opml.opml", atom_content=atom_content, rows=rows),
            200,
            {"Content-Type": "text/plain"},
        )


# False negatives
@app.route("/taint")
def taint():
    name = request.args.get("name")
    safe_name = flask.Markup.escape(name)
    return render_template("unsafe.txt", name=safe_name)
