"""Unit tests for OpenSourceMalwareClient — HTTP layer mocked, no network."""

from unittest.mock import MagicMock

import requests

from client import OpenSourceMalwareClient


class _DummyHelper:
    class _Logger:
        def info(self, *a, **k): ...
        def error(self, *a, **k): ...

    connector_logger = _Logger()


def _client():
    return OpenSourceMalwareClient(_DummyHelper(), "https://api.example.com/v1/", "tok")


def _response(json_data, status=200):
    resp = MagicMock()
    resp.json.return_value = json_data
    resp.raise_for_status.return_value = None
    resp.status_code = status
    return resp


def test_base_url_trailing_slash_stripped():
    assert _client().base_url == "https://api.example.com/v1"


def test_auth_header_set():
    client = _client()
    assert client.session.headers["Authorization"] == "Bearer tok"


def test_query_latest_returns_threats_list():
    client = _client()
    client.session.get = MagicMock(
        return_value=_response({"threats": [{"id": "1"}, {"id": "2"}]})
    )
    assert client.query_latest("npm") == [{"id": "1"}, {"id": "2"}]
    # The ecosystem is passed through as a query param.
    _, kwargs = client.session.get.call_args
    assert kwargs["params"] == {"ecosystem": "npm"}


def test_query_latest_empty_when_no_threats_key():
    client = _client()
    client.session.get = MagicMock(return_value=_response({"foo": "bar"}))
    assert client.query_latest("npm") == []


def test_query_latest_handles_api_error_field():
    client = _client()
    client.session.get = MagicMock(return_value=_response({"error": "rate limited"}))
    assert client.query_latest("npm") == []


def test_query_latest_handles_request_exception():
    client = _client()
    client.session.get = MagicMock(side_effect=requests.RequestException("boom"))
    assert client.query_latest("npm") == []


def test_query_latest_handles_http_error_status():
    client = _client()
    resp = _response({}, status=500)
    resp.raise_for_status.side_effect = requests.HTTPError("500")
    client.session.get = MagicMock(return_value=resp)
    assert client.query_latest("npm") == []
