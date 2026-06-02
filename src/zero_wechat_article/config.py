"""Load credentials from environment."""

from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass(frozen=True)
class WeChatConfig:
    app_id: str
    app_secret: str

    @classmethod
    def from_env(cls) -> WeChatConfig:
        app_id = os.environ.get("WECHAT_MP_APPID", "").strip()
        app_secret = os.environ.get("WECHAT_MP_SECRET", "").strip()
        if not app_id or not app_secret:
            raise ValueError(
                "WECHAT_MP_APPID and WECHAT_MP_SECRET must be set (see .env.example)"
            )
        return cls(app_id=app_id, app_secret=app_secret)

    @property
    def confirm_publish(self) -> bool:
        return os.environ.get("CONFIRM_PUBLISH", "0").strip() in ("1", "true", "yes")
