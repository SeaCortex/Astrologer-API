"""
This is part of Astrologer API (C) 2023 Giacomo Battaglia
"""

from starlette.datastructures import Headers
from starlette.responses import JSONResponse
from starlette.types import ASGIApp, Receive, Scope, Send
import logging


class SecretKeyCheckerMiddleware:
    def __init__(self, app: ASGIApp, secret_key_name: str, secret_keys: list = []) -> None:
        self.app = app
        self.secret_key_values = [key for key in secret_keys if key]
        self.secret_key_name = secret_key_name
        self.pass_all = False

        if not self.secret_key_name or not self.secret_key_values:
            logging.critical("Secret key name or secret key values not set. The middleware will let all requests pass through!")
            self.pass_all = True

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        if self.pass_all:
            await self.app(scope, receive, send)
            return

        headers = Headers(scope=scope)
        header_key = headers.get(self.secret_key_name, "").split(":")[0]

        if header_key in self.secret_key_values:
            await self.app(scope, receive, send)
        else:
            response = JSONResponse(
                status_code=403,
                content={"status": "KO", "message": "Forbidden: Invalid or missing secret key"},
            )
            await response(scope, receive, send)
