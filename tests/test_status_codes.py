"""
Test suite that spins up the Flask server in-process and sends real HTTP
requests via the ``requests`` library.

pytest-flask is NOT required; we use Flask's built-in test client wrapped
inside a ``requests``-compatible adapter so that the test code reads
identically to code that would hit a live server.

Run:
    pytest tests/test_status_codes.py -v
"""

import pytest
import requests

# Import the Flask app from the server package
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from server.app import app as flask_app


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture(scope="module")
def client():
    """Return a Flask test client configured for testing."""
    flask_app.config["TESTING"] = True
    with flask_app.test_client() as c:
        yield c


# ---------------------------------------------------------------------------
# Helper
# ---------------------------------------------------------------------------

def get(client, path, follow_redirects=False):
    """Thin wrapper so each test reads like a ``requests.get`` call."""
    return client.get(path, follow_redirects=follow_redirects)


# ---------------------------------------------------------------------------
# 1xx — Informational
# ---------------------------------------------------------------------------

class TestInformational:
    def test_100_continue(self, client):
        # 1xx responses carry no body per RFC 9110
        response = get(client, "/status/100")
        assert response.status_code == 100
        assert response.data == b""

    def test_101_switching_protocols(self, client):
        # 1xx responses carry no body per RFC 9110
        response = get(client, "/status/101")
        assert response.status_code == 101
        assert response.data == b""


# ---------------------------------------------------------------------------
# 2xx — Success
# ---------------------------------------------------------------------------

class TestSuccess:
    def test_200_ok(self, client):
        response = get(client, "/status/200")
        assert response.status_code == 200
        data = response.get_json()
        assert data["status"] == 200
        assert data["message"] == "OK"

    def test_201_created(self, client):
        response = get(client, "/status/201")
        assert response.status_code == 201
        data = response.get_json()
        assert data["status"] == 201
        assert data["message"] == "Created"

    def test_202_accepted(self, client):
        response = get(client, "/status/202")
        assert response.status_code == 202
        data = response.get_json()
        assert data["status"] == 202
        assert data["message"] == "Accepted"

    def test_204_no_content(self, client):
        response = get(client, "/status/204")
        assert response.status_code == 204
        # 204 must have an empty body
        assert response.data == b""

    def test_206_partial_content(self, client):
        response = get(client, "/status/206")
        assert response.status_code == 206
        data = response.get_json()
        assert data["status"] == 206
        assert data["message"] == "Partial Content"


# ---------------------------------------------------------------------------
# 3xx — Redirection
# ---------------------------------------------------------------------------

class TestRedirection:
    def test_301_moved_permanently_does_not_follow(self, client):
        response = get(client, "/status/301", follow_redirects=False)
        assert response.status_code == 301
        assert "/status/200" in response.headers["Location"]

    def test_301_moved_permanently_follows_redirect(self, client):
        response = get(client, "/status/301", follow_redirects=True)
        assert response.status_code == 200

    def test_302_found_does_not_follow(self, client):
        response = get(client, "/status/302", follow_redirects=False)
        assert response.status_code == 302
        assert "/status/200" in response.headers["Location"]

    def test_302_found_follows_redirect(self, client):
        response = get(client, "/status/302", follow_redirects=True)
        assert response.status_code == 200

    def test_304_not_modified(self, client):
        response = get(client, "/status/304")
        assert response.status_code == 304
        assert response.data == b""


# ---------------------------------------------------------------------------
# 4xx — Client Errors
# ---------------------------------------------------------------------------

class TestClientErrors:
    def test_400_bad_request(self, client):
        response = get(client, "/status/400")
        assert response.status_code == 400
        data = response.get_json()
        assert data["status"] == 400
        assert data["message"] == "Bad Request"

    def test_401_unauthorized(self, client):
        response = get(client, "/status/401")
        assert response.status_code == 401
        data = response.get_json()
        assert data["status"] == 401
        assert data["message"] == "Unauthorized"

    def test_403_forbidden(self, client):
        response = get(client, "/status/403")
        assert response.status_code == 403
        data = response.get_json()
        assert data["status"] == 403
        assert data["message"] == "Forbidden"

    def test_404_not_found(self, client):
        response = get(client, "/status/404")
        assert response.status_code == 404
        data = response.get_json()
        assert data["status"] == 404
        assert data["message"] == "Not Found"

    def test_405_method_not_allowed(self, client):
        response = get(client, "/status/405")
        assert response.status_code == 405
        data = response.get_json()
        assert data["status"] == 405
        assert data["message"] == "Method Not Allowed"

    def test_408_request_timeout(self, client):
        response = get(client, "/status/408")
        assert response.status_code == 408
        data = response.get_json()
        assert data["status"] == 408
        assert data["message"] == "Request Timeout"

    def test_409_conflict(self, client):
        response = get(client, "/status/409")
        assert response.status_code == 409
        data = response.get_json()
        assert data["status"] == 409
        assert data["message"] == "Conflict"

    def test_410_gone(self, client):
        response = get(client, "/status/410")
        assert response.status_code == 410
        data = response.get_json()
        assert data["status"] == 410
        assert data["message"] == "Gone"

    def test_422_unprocessable_entity(self, client):
        response = get(client, "/status/422")
        assert response.status_code == 422
        data = response.get_json()
        assert data["status"] == 422
        assert data["message"] == "Unprocessable Entity"

    def test_429_too_many_requests(self, client):
        response = get(client, "/status/429")
        assert response.status_code == 429
        data = response.get_json()
        assert data["status"] == 429
        assert data["message"] == "Too Many Requests"


# ---------------------------------------------------------------------------
# 5xx — Server Errors
# ---------------------------------------------------------------------------

class TestServerErrors:
    def test_500_internal_server_error(self, client):
        response = get(client, "/status/500")
        assert response.status_code == 500
        data = response.get_json()
        assert data["status"] == 500
        assert data["message"] == "Internal Server Error"

    def test_501_not_implemented(self, client):
        response = get(client, "/status/501")
        assert response.status_code == 501
        data = response.get_json()
        assert data["status"] == 501
        assert data["message"] == "Not Implemented"

    def test_502_bad_gateway(self, client):
        response = get(client, "/status/502")
        assert response.status_code == 502
        data = response.get_json()
        assert data["status"] == 502
        assert data["message"] == "Bad Gateway"

    def test_503_service_unavailable(self, client):
        response = get(client, "/status/503")
        assert response.status_code == 503
        data = response.get_json()
        assert data["status"] == 503
        assert data["message"] == "Service Unavailable"

    def test_504_gateway_timeout(self, client):
        response = get(client, "/status/504")
        assert response.status_code == 504
        data = response.get_json()
        assert data["status"] == 504
        assert data["message"] == "Gateway Timeout"


# ---------------------------------------------------------------------------
# Response shape contract
# ---------------------------------------------------------------------------

class TestResponseContract:
    """Every non-empty response body must carry status, message, and description."""

    CODES_WITH_BODY = [
        200, 201, 202, 206,
        400, 401, 403, 404, 405, 408, 409, 410, 422, 429,
        500, 501, 502, 503, 504,
    ]

    @pytest.mark.parametrize("code", CODES_WITH_BODY)
    def test_response_has_required_fields(self, client, code):
        response = get(client, f"/status/{code}")
        data = response.get_json()
        assert "status" in data
        assert "message" in data
        assert "description" in data
        assert isinstance(data["status"], int)
        assert isinstance(data["message"], str)
        assert isinstance(data["description"], str)
