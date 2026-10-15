"""Tests for the BoltzmannClient HTTP wrapper."""

import pytest
from unittest.mock import MagicMock

from boltzmann_cli.client import (
    BoltzmannClient,
    AuthError,
    APIError,
)


def _mock_response(status_code, json_data=None, text=""):
    resp = MagicMock()
    resp.status_code = status_code
    resp.text = text
    resp.json.return_value = json_data or {}
    return resp


class TestHeaders:
    def test_api_key_uses_apikey_scheme(self):
        client = BoltzmannClient("http://localhost:8009", api_key="test-key")
        headers = client._headers()
        assert headers["Authorization"] == "ApiKey test-key"

    def test_token_uses_bearer_scheme(self):
        client = BoltzmannClient("http://localhost:8009", token="jwt-token")
        headers = client._headers()
        assert headers["Authorization"] == "Bearer jwt-token"

    def test_api_key_takes_precedence_over_token(self):
        client = BoltzmannClient("http://localhost:8009", token="jwt", api_key="key")
        assert client._headers()["Authorization"] == "ApiKey key"

    def test_no_auth_header_when_unauthenticated(self):
        client = BoltzmannClient("http://localhost:8009")
        assert "Authorization" not in client._headers()

    def test_strips_trailing_slash(self):
        client = BoltzmannClient("http://localhost:8009/")
        assert client.api_url == "http://localhost:8009"


class TestHandleResponse:
    def setup_method(self):
        self.client = BoltzmannClient("http://localhost:8009", api_key="k")

    def test_returns_json_on_success(self):
        resp = _mock_response(200, {"data": "ok"})
        assert self.client._handle(resp) == {"data": "ok"}

    def test_returns_none_on_204(self):
        resp = _mock_response(204)
        assert self.client._handle(resp) is None

    def test_raises_auth_error_on_401(self):
        resp = _mock_response(401)
        with pytest.raises(AuthError):
            self.client._handle(resp)

    def test_raises_api_error_on_500(self):
        resp = _mock_response(500, {"detail": "Internal error"})
        with pytest.raises(APIError, match="500"):
            self.client._handle(resp)

    def test_raises_api_error_on_404(self):
        resp = _mock_response(404, {"detail": "missing"})
        with pytest.raises(APIError) as exc_info:
            self.client._handle(resp)
        assert exc_info.value.status_code == 404

    def test_handles_non_json_error_body(self):
        resp = _mock_response(502, text="Bad Gateway")
        resp.json.side_effect = Exception("not json")
        with pytest.raises(APIError, match="Bad Gateway"):
            self.client._handle(resp)
