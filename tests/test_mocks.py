"""
Test suite using the ``responses`` library to mock HTTP calls.

These tests demonstrate how to intercept outgoing ``requests`` calls and
return pre-configured HTTP responses — no running server required.  This
pattern is useful when testing code that *consumes* an HTTP API and you want
to verify that your client handles every possible status code correctly.

Run:
    pytest tests/test_mocks.py -v
"""

import pytest
import requests
import responses as rsps_lib

BASE_URL = "https://example-api.test"


# ---------------------------------------------------------------------------
# Helper — a tiny client that wraps requests and classifies responses
# ---------------------------------------------------------------------------

def fetch(url: str, allow_redirects: bool = True) -> dict:
    """
    Fetch *url* and return a dict with::

        {
          "status_code": int,
          "ok":          bool,   # True for 2xx
          "json":        dict | None,
          "redirected":  bool,   # True when a redirect was followed
        }
    """
    response = requests.get(url, allow_redirects=allow_redirects)
    try:
        body = response.json()
    except Exception:
        body = None
    return {
        "status_code": response.status_code,
        "ok": response.ok,
        "json": body,
        "redirected": len(response.history) > 0,
    }


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture(autouse=True)
def mock_requests():
    """Activate the ``responses`` mock for every test in this module."""
    with rsps_lib.RequestsMock(assert_all_requests_are_fired=True) as mock:
        yield mock


# ---------------------------------------------------------------------------
# 1xx — Informational
# ---------------------------------------------------------------------------

class TestInformationalMocks:
    def test_100_continue(self, mock_requests):
        # 1xx responses carry no body per RFC 9110
        mock_requests.add(rsps_lib.GET, f"{BASE_URL}/status/100", status=100, body=b"")
        result = fetch(f"{BASE_URL}/status/100")
        assert result["status_code"] == 100
        assert result["json"] is None

    def test_101_switching_protocols(self, mock_requests):
        # 1xx responses carry no body per RFC 9110
        mock_requests.add(rsps_lib.GET, f"{BASE_URL}/status/101", status=101, body=b"")
        result = fetch(f"{BASE_URL}/status/101")
        assert result["status_code"] == 101
        assert result["json"] is None


# ---------------------------------------------------------------------------
# 2xx — Success
# ---------------------------------------------------------------------------

class TestSuccessMocks:
    def test_200_ok(self, mock_requests):
        mock_requests.add(rsps_lib.GET, f"{BASE_URL}/status/200", status=200,
                          json={"status": 200, "message": "OK", "description": "The request succeeded."})
        result = fetch(f"{BASE_URL}/status/200")
        assert result["status_code"] == 200
        assert result["ok"] is True
        assert result["json"]["message"] == "OK"

    def test_201_created(self, mock_requests):
        mock_requests.add(rsps_lib.GET, f"{BASE_URL}/status/201", status=201,
                          json={"status": 201, "message": "Created",
                                "description": "A new resource has been successfully created."})
        result = fetch(f"{BASE_URL}/status/201")
        assert result["status_code"] == 201
        assert result["ok"] is True
        assert result["json"]["message"] == "Created"

    def test_202_accepted(self, mock_requests):
        mock_requests.add(rsps_lib.GET, f"{BASE_URL}/status/202", status=202,
                          json={"status": 202, "message": "Accepted",
                                "description": "The request has been accepted for processing."})
        result = fetch(f"{BASE_URL}/status/202")
        assert result["status_code"] == 202
        assert result["ok"] is True

    def test_204_no_content(self, mock_requests):
        mock_requests.add(rsps_lib.GET, f"{BASE_URL}/status/204", status=204, body=b"")
        result = fetch(f"{BASE_URL}/status/204")
        assert result["status_code"] == 204
        assert result["ok"] is True
        assert result["json"] is None  # no body

    def test_206_partial_content(self, mock_requests):
        mock_requests.add(rsps_lib.GET, f"{BASE_URL}/status/206", status=206,
                          json={"status": 206, "message": "Partial Content",
                                "description": "Delivering only part of the resource."})
        result = fetch(f"{BASE_URL}/status/206")
        assert result["status_code"] == 206
        assert result["ok"] is True


# ---------------------------------------------------------------------------
# 3xx — Redirection
# ---------------------------------------------------------------------------

class TestRedirectionMocks:
    def test_301_without_following(self, mock_requests):
        mock_requests.add(rsps_lib.GET, f"{BASE_URL}/status/301", status=301,
                          headers={"Location": f"{BASE_URL}/status/200"})
        result = fetch(f"{BASE_URL}/status/301", allow_redirects=False)
        assert result["status_code"] == 301
        assert result["redirected"] is False

    def test_301_following_redirect(self, mock_requests):
        mock_requests.add(rsps_lib.GET, f"{BASE_URL}/status/301", status=301,
                          headers={"Location": f"{BASE_URL}/status/200"})
        mock_requests.add(rsps_lib.GET, f"{BASE_URL}/status/200", status=200,
                          json={"status": 200, "message": "OK", "description": "The request succeeded."})
        result = fetch(f"{BASE_URL}/status/301", allow_redirects=True)
        assert result["status_code"] == 200
        assert result["redirected"] is True

    def test_302_without_following(self, mock_requests):
        mock_requests.add(rsps_lib.GET, f"{BASE_URL}/status/302", status=302,
                          headers={"Location": f"{BASE_URL}/status/200"})
        result = fetch(f"{BASE_URL}/status/302", allow_redirects=False)
        assert result["status_code"] == 302

    def test_304_not_modified(self, mock_requests):
        mock_requests.add(rsps_lib.GET, f"{BASE_URL}/status/304", status=304, body=b"")
        result = fetch(f"{BASE_URL}/status/304")
        assert result["status_code"] == 304
        assert result["json"] is None


# ---------------------------------------------------------------------------
# 4xx — Client Errors
# ---------------------------------------------------------------------------

class TestClientErrorMocks:
    @pytest.mark.parametrize("code,message", [
        (400, "Bad Request"),
        (401, "Unauthorized"),
        (403, "Forbidden"),
        (404, "Not Found"),
        (405, "Method Not Allowed"),
        (408, "Request Timeout"),
        (409, "Conflict"),
        (410, "Gone"),
        (422, "Unprocessable Entity"),
        (429, "Too Many Requests"),
    ])
    def test_client_error(self, mock_requests, code, message):
        mock_requests.add(rsps_lib.GET, f"{BASE_URL}/status/{code}", status=code,
                          json={"status": code, "message": message, "description": "A client error."})
        result = fetch(f"{BASE_URL}/status/{code}")
        assert result["status_code"] == code
        assert result["ok"] is False  # 4xx is never "ok"
        assert result["json"]["message"] == message


# ---------------------------------------------------------------------------
# 5xx — Server Errors
# ---------------------------------------------------------------------------

class TestServerErrorMocks:
    @pytest.mark.parametrize("code,message", [
        (500, "Internal Server Error"),
        (501, "Not Implemented"),
        (502, "Bad Gateway"),
        (503, "Service Unavailable"),
        (504, "Gateway Timeout"),
    ])
    def test_server_error(self, mock_requests, code, message):
        mock_requests.add(rsps_lib.GET, f"{BASE_URL}/status/{code}", status=code,
                          json={"status": code, "message": message, "description": "A server error."})
        result = fetch(f"{BASE_URL}/status/{code}")
        assert result["status_code"] == code
        assert result["ok"] is False  # 5xx is never "ok"
        assert result["json"]["message"] == message


# ---------------------------------------------------------------------------
# Connection / network-level errors
# ---------------------------------------------------------------------------

class TestNetworkErrors:
    def test_connection_error(self, mock_requests):
        """Verify that a ConnectionError is raised when the host is unreachable."""
        mock_requests.add(rsps_lib.GET, f"{BASE_URL}/status/connect-error",
                          body=requests.exceptions.ConnectionError("Connection refused"))
        with pytest.raises(requests.exceptions.ConnectionError):
            fetch(f"{BASE_URL}/status/connect-error")

    def test_timeout_error(self, mock_requests):
        """Verify that a Timeout exception propagates correctly."""
        mock_requests.add(rsps_lib.GET, f"{BASE_URL}/status/timeout",
                          body=requests.exceptions.Timeout("Request timed out"))
        with pytest.raises(requests.exceptions.Timeout):
            fetch(f"{BASE_URL}/status/timeout")
