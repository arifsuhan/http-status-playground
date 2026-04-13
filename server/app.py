"""
Flask server for the HTTP status code playground.

Each route returns the HTTP status code indicated by its path, along with a
JSON body that describes the code and its conventional meaning.  The server is
intentionally minimal — its only purpose is to make every major status code
reachable so that the test suite (and curious humans) can observe real HTTP
responses.

Run locally:
    python server/app.py

The server will listen on http://127.0.0.1:5000 by default.
"""

from flask import Flask, jsonify, redirect

app = Flask(__name__)


def _response(code: int, message: str, description: str):
    """Build a uniform JSON response for a given status code."""
    body = {"status": code, "message": message, "description": description}
    return jsonify(body), code


# ---------------------------------------------------------------------------
# 1xx — Informational
# ---------------------------------------------------------------------------

@app.route("/status/100")
def status_100():
    """100 Continue — the client should continue with its request.

    RFC 9110 §15.2.1: informational responses MUST NOT include a body.
    """
    return "", 100


@app.route("/status/101")
def status_101():
    """101 Switching Protocols — the server is switching protocols.

    RFC 9110 §15.2.2: informational responses MUST NOT include a body.
    """
    return "", 101


# ---------------------------------------------------------------------------
# 2xx — Success
# ---------------------------------------------------------------------------

@app.route("/status/200")
def status_200():
    """200 OK — the standard success response."""
    return _response(200, "OK", "The request succeeded.")


@app.route("/status/201")
def status_201():
    """201 Created — a resource was successfully created."""
    return _response(201, "Created", "A new resource has been successfully created.")


@app.route("/status/202")
def status_202():
    """202 Accepted — the request has been accepted for processing."""
    return _response(202, "Accepted", "The request has been accepted for processing but has not been completed.")


@app.route("/status/204")
def status_204():
    """204 No Content — success with no response body."""
    # 204 must not include a message body
    return "", 204


@app.route("/status/206")
def status_206():
    """206 Partial Content — the server is returning a partial resource."""
    return _response(206, "Partial Content", "The server is delivering only part of the resource due to a range header.")


# ---------------------------------------------------------------------------
# 3xx — Redirection
# ---------------------------------------------------------------------------

@app.route("/status/301")
def status_301():
    """301 Moved Permanently — the resource has a new permanent URL."""
    return redirect("/status/200", code=301)


@app.route("/status/302")
def status_302():
    """302 Found — the resource temporarily resides at a different URL."""
    return redirect("/status/200", code=302)


@app.route("/status/304")
def status_304():
    """304 Not Modified — the cached version is still valid."""
    return "", 304


# ---------------------------------------------------------------------------
# 4xx — Client Errors
# ---------------------------------------------------------------------------

@app.route("/status/400")
def status_400():
    """400 Bad Request — the server cannot process the malformed request."""
    return _response(400, "Bad Request", "The server could not understand the request due to invalid syntax.")


@app.route("/status/401")
def status_401():
    """401 Unauthorized — authentication is required."""
    return _response(401, "Unauthorized", "Authentication is required and has failed or has not been provided.")


@app.route("/status/403")
def status_403():
    """403 Forbidden — the server refuses to authorize the request."""
    return _response(403, "Forbidden", "You do not have permission to access this resource.")


@app.route("/status/404")
def status_404():
    """404 Not Found — the resource could not be found."""
    return _response(404, "Not Found", "The requested resource could not be found on this server.")


@app.route("/status/405")
def status_405():
    """405 Method Not Allowed — the HTTP method is not supported."""
    return _response(405, "Method Not Allowed", "The request method is not supported for the requested resource.")


@app.route("/status/408")
def status_408():
    """408 Request Timeout — the server timed out waiting for the request."""
    return _response(408, "Request Timeout", "The server timed out waiting for the request.")


@app.route("/status/409")
def status_409():
    """409 Conflict — the request conflicts with the current state."""
    return _response(409, "Conflict", "The request could not be completed due to a conflict with the current state of the resource.")


@app.route("/status/410")
def status_410():
    """410 Gone — the resource has been permanently deleted."""
    return _response(410, "Gone", "The resource has been permanently removed and will not be available again.")


@app.route("/status/422")
def status_422():
    """422 Unprocessable Entity — validation errors prevented processing."""
    return _response(422, "Unprocessable Entity", "The request was well-formed but contains semantic errors.")


@app.route("/status/429")
def status_429():
    """429 Too Many Requests — the client has sent too many requests."""
    return _response(429, "Too Many Requests", "You have sent too many requests in a given amount of time.")


# ---------------------------------------------------------------------------
# 5xx — Server Errors
# ---------------------------------------------------------------------------

@app.route("/status/500")
def status_500():
    """500 Internal Server Error — a generic server-side error."""
    return _response(500, "Internal Server Error", "The server encountered an unexpected condition.")


@app.route("/status/501")
def status_501():
    """501 Not Implemented — the server does not support this functionality."""
    return _response(501, "Not Implemented", "The request method is not supported by the server.")


@app.route("/status/502")
def status_502():
    """502 Bad Gateway — an upstream server returned an invalid response."""
    return _response(502, "Bad Gateway", "The server received an invalid response from an upstream server.")


@app.route("/status/503")
def status_503():
    """503 Service Unavailable — the server is temporarily unavailable."""
    return _response(503, "Service Unavailable", "The server is temporarily unable to handle the request.")


@app.route("/status/504")
def status_504():
    """504 Gateway Timeout — an upstream server did not respond in time."""
    return _response(504, "Gateway Timeout", "The server did not receive a timely response from an upstream server.")


if __name__ == "__main__":
    app.run(debug=False)
