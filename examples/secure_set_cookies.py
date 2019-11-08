# secure is not set, httponly is not set, samesite is not set
def none_set():
    import flask

    response = flask.make_response()
    response.set_cookie("cookie_name", "cookie_value")


def some_set():
    from flask import make_response

    r = make_response()

    # some values are set but not others
    r.set_cookie("cookie1", "cookie_value", secure=True)
    r.set_cookie("cookie2", "cookie_value", httponly=True)
    r.set_cookie("cookie3", "cookie_value", samesite="Lax")
    r.set_cookie("cookie4", "cookie_value", secure=True, httponly=True)
    r.set_cookie("cookie5", "cookie_value", httponly=True, samesite="Lax")

    # explicitly disabled
    r.set_cookie("cookie6", "cookie_value", secure=False)
    r.set_cookie("cookie7", "cookie_value", httponly=False)
    r.set_cookie("cookie8", "cookie_value", samesite=None)
    r.set_cookie("cookie9", "cookie_value", secure=False, httponly=False)
    r.set_cookie("cookie10", "cookie_value", httponly=False, samesite=None)
