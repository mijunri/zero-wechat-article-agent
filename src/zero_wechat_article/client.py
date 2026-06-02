"""Minimal WeChat MP API client (token + draft stubs)."""

from __future__ import annotations

import time
from typing import Any

import httpx

from zero_wechat_article.config import WeChatConfig

API_BASE = "https://api.weixin.qq.com/cgi-bin"


class WeChatMPClient:
    def __init__(self, config: WeChatConfig | None = None) -> None:
        self._config = config or WeChatConfig.from_env()
        self._token: str | None = None
        self._token_expires_at: float = 0.0

    def get_access_token(self, force: bool = False) -> str:
        if not force and self._token and time.time() < self._token_expires_at - 60:
            return self._token

        url = f"{API_BASE}/token"
        params = {
            "grant_type": "client_credential",
            "appid": self._config.app_id,
            "secret": self._config.app_secret,
        }
        with httpx.Client(timeout=30.0) as client:
            resp = client.get(url, params=params)
            resp.raise_for_status()
            data: dict[str, Any] = resp.json()

        if "errcode" in data and data["errcode"] != 0:
            raise RuntimeError(f"WeChat token error: {data}")
        if "access_token" not in data:
            raise RuntimeError(f"Unexpected token response: {data}")

        self._token = str(data["access_token"])
        self._token_expires_at = time.time() + int(data.get("expires_in", 7200))
        return self._token

    def api_get(self, path: str, **params: Any) -> dict[str, Any]:
        token = self.get_access_token()
        url = f"{API_BASE}/{path.lstrip('/')}"
        with httpx.Client(timeout=60.0) as client:
            resp = client.get(url, params={"access_token": token, **params})
            resp.raise_for_status()
            return resp.json()

    def api_post(self, path: str, json_body: dict[str, Any]) -> dict[str, Any]:
        token = self.get_access_token()
        url = f"{API_BASE}/{path.lstrip('/')}"
        with httpx.Client(timeout=120.0) as client:
            resp = client.post(url, params={"access_token": token}, json=json_body)
            resp.raise_for_status()
            return resp.json()
