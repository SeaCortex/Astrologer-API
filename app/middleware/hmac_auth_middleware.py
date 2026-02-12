"""
HMAC authentication middleware for internal service-to-service requests.
"""

from __future__ import annotations

import base64
import hashlib
import hmac
import logging
import time
from typing import Optional

from starlette.datastructures import Headers
from starlette.responses import JSONResponse
from starlette.types import ASGIApp, Receive, Scope, Send

logger = logging.getLogger(__name__)


class HMACAuthMiddleware:
    def __init__(
        self,
        app: ASGIApp,
        *,
        hmac_secret: str,
        hmac_secrets: dict[str, str],
        signature_header: str = "X-Signature",
        timestamp_header: str = "X-Timestamp",
        key_id_header: str = "X-Key-Id",
        timestamp_skew_seconds: int = 300,
        excluded_paths: Optional[list[str]] = None,
    ) -> None:
        self.app = app
        self.hmac_secret = hmac_secret
        self.hmac_secrets = hmac_secrets or {}
        self.signature_header = signature_header
        self.timestamp_header = timestamp_header
        self.key_id_header = key_id_header
        self.timestamp_skew_seconds = timestamp_skew_seconds
        self.excluded_paths = set(excluded_paths or ["/health"])

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        path = scope.get("path", "")
        if path in self.excluded_paths:
            await self.app(scope, receive, send)
            return

        headers = Headers(scope=scope)
        timestamp_value = headers.get(self.timestamp_header, "")
        signature_value = headers.get(self.signature_header, "")
        key_id_value = headers.get(self.key_id_header, "")

        secret = self._resolve_secret(key_id_value)
        if not secret:
            await self._reject(scope, receive, send, 401, "Unauthorized - missing or invalid HMAC key")
            return

        try:
            timestamp = int(timestamp_value)
        except (TypeError, ValueError):
            await self._reject(scope, receive, send, 401, "Unauthorized - invalid timestamp")
            return

        if not self._timestamp_within_skew(timestamp):
            await self._reject(scope, receive, send, 401, "Unauthorized - timestamp outside allowed skew")
            return

        body = await self._read_body(receive)
        expected_hex, expected_b64 = self._compute_signatures(
            secret=secret,
            timestamp=timestamp_value,
            method=scope.get("method", "GET"),
            path=path,
            query_string=scope.get("query_string", b""),
            body=body,
        )

        if not signature_value or not (
            hmac.compare_digest(signature_value, expected_hex)
            or hmac.compare_digest(signature_value, expected_b64)
        ):
            await self._reject(scope, receive, send, 401, "Unauthorized - invalid signature")
            return

        body_consumed = False

        async def receive_with_body() -> dict:
            nonlocal body_consumed
            if body_consumed:
                return {"type": "http.request", "body": b"", "more_body": False}
            body_consumed = True
            return {"type": "http.request", "body": body, "more_body": False}

        await self.app(scope, receive_with_body, send)

    def _resolve_secret(self, key_id: str) -> Optional[str]:
        if key_id:
            return self.hmac_secrets.get(key_id)
        if self.hmac_secret:
            return self.hmac_secret
        if len(self.hmac_secrets) == 1:
            return next(iter(self.hmac_secrets.values()))
        return None

    def _timestamp_within_skew(self, timestamp: int) -> bool:
        now = int(time.time())
        return abs(now - timestamp) <= self.timestamp_skew_seconds

    async def _read_body(self, receive: Receive) -> bytes:
        body = b""
        more_body = True
        while more_body:
            message = await receive()
            if message["type"] != "http.request":
                continue
            body += message.get("body", b"")
            more_body = message.get("more_body", False)
        return body

    def _compute_signatures(
        self,
        *,
        secret: str,
        timestamp: str,
        method: str,
        path: str,
        query_string: bytes,
        body: bytes,
    ) -> tuple[str, str]:
        query = query_string.decode()
        path_with_query = f"{path}?{query}" if query else path
        body_hash = hashlib.sha256(body).hexdigest()
        canonical = f"{timestamp}\n{method.upper()}\n{path_with_query}\n{body_hash}"
        digest = hmac.new(
            secret.encode("utf-8"),
            canonical.encode("utf-8"),
            hashlib.sha256,
        ).digest()
        expected_hex = digest.hex()
        expected_b64 = base64.b64encode(digest).decode("ascii")
        return expected_hex, expected_b64

    async def _reject(self, scope: Scope, receive: Receive, send: Send, status_code: int, message: str) -> None:
        logger.warning("HMAC auth failed: %s", message)
        response = JSONResponse(status_code=status_code, content={"status": "KO", "message": message})
        await response(scope, receive, send)
