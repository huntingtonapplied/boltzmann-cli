"""BoltzmannClient — centralized HTTP client with retry and error hints."""

import os
import time
from typing import Any, Dict, Optional

import requests
from requests.exceptions import ConnectionError, Timeout

MAX_RETRIES = int(os.getenv("BOLTZMANN_MAX_RETRIES", "3"))
_BACKOFF_BASE = 0.5
_BACKOFF_MAX = 10.0
_RETRYABLE = {429, 500, 502, 503, 504}

_HINTS: Dict[int, str] = {
    401: "Set BOLTZMANN_API_KEY or run: boltzmann login",
    403: "You don't have permission for this resource.",
    404: "Resource not found — check the ID.",
    422: "Invalid request data — check your inputs.",
    429: "Rate limit hit — wait a moment and retry.",
    500: "Server error — try again in a few minutes.",
}


class AuthError(Exception):
    pass


class APIError(Exception):
    def __init__(self, message: str, status_code: int = 0):
        super().__init__(message)
        self.status_code = status_code


class BoltzmannClient:
    """Thin HTTP client for the Boltzmann API.

    Supports both Bearer (JWT) and ApiKey auth schemes.
    Retries transient failures with exponential backoff.
    """

    def __init__(
        self,
        api_url: str,
        token: Optional[str] = None,
        api_key: Optional[str] = None,
    ):
        self.api_url = api_url.rstrip("/")
        self.token = token
        self.api_key = api_key
        self._timeout = float(os.getenv("BOLTZMANN_TIMEOUT", "30"))

    def _headers(self) -> Dict[str, str]:
        headers = {"Content-Type": "application/json"}
        if self.api_key:
            headers["Authorization"] = f"ApiKey {self.api_key}"
        elif self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        return headers

    def _request(self, method: str, path: str, **kwargs) -> requests.Response:
        url = f"{self.api_url}{path}"
        last_exc: Optional[Exception] = None
        for attempt in range(MAX_RETRIES + 1):
            try:
                resp = requests.request(
                    method, url, headers=self._headers(), timeout=self._timeout, **kwargs
                )
                if resp.status_code not in _RETRYABLE or attempt == MAX_RETRIES:
                    return resp
                time.sleep(min(_BACKOFF_BASE * (2**attempt), _BACKOFF_MAX))
            except (ConnectionError, Timeout) as exc:
                last_exc = exc
                if attempt == MAX_RETRIES:
                    raise APIError(f"Connection failed: {exc}")
                time.sleep(min(_BACKOFF_BASE * (2**attempt), _BACKOFF_MAX))
        raise APIError("Request failed after retries")

    def _handle(self, resp: requests.Response) -> Any:
        if resp.status_code == 401:
            raise AuthError(f"Not authenticated.\n  {_HINTS[401]}")
        if resp.status_code == 204:
            return None
        if resp.status_code >= 400:
            try:
                detail = resp.json().get("detail", resp.text)
            except Exception:
                detail = resp.text
            hint = _HINTS.get(resp.status_code, "")
            suffix = f"\n  {hint}" if hint else ""
            raise APIError(f"API error {resp.status_code}: {detail}{suffix}", resp.status_code)
        return resp.json()

    def get(self, path: str, params=None) -> Any:
        return self._handle(self._request("GET", path, params=params))

    def post(self, path: str, data=None) -> Any:
        return self._handle(self._request("POST", path, json=data))

    def patch(self, path: str, data=None) -> Any:
        return self._handle(self._request("PATCH", path, json=data))

    def delete(self, path: str) -> Any:
        return self._handle(self._request("DELETE", path))
