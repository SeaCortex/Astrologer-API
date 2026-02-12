import hashlib
import hmac
import json
import time

from fastapi import FastAPI
from fastapi.responses import JSONResponse
from fastapi.testclient import TestClient

from app.middleware.hmac_auth_middleware import HMACAuthMiddleware


def _sign_request(timestamp: str, method: str, path_with_query: str, body: bytes, secret: str) -> str:
    body_hash = hashlib.sha256(body).hexdigest()
    canonical = f"{timestamp}\n{method}\n{path_with_query}\n{body_hash}"
    return hmac.new(secret.encode("utf-8"), canonical.encode("utf-8"), hashlib.sha256).hexdigest()


def _build_client(secret: str) -> TestClient:
    app = FastAPI()
    app.add_middleware(
        HMACAuthMiddleware,
        hmac_secret=secret,
        hmac_secrets={},
        signature_header="X-Signature",
        timestamp_header="X-Timestamp",
        key_id_header="X-Key-Id",
        timestamp_skew_seconds=300,
        excluded_paths=["/health"],
    )

    @app.post("/protected")
    def protected(payload: dict) -> JSONResponse:
        return JSONResponse(content={"status": "OK", "payload": payload})

    @app.get("/health")
    def health() -> JSONResponse:
        return JSONResponse(content={"status": "OK"})

    return TestClient(app)


def test_hmac_valid_signature() -> None:
    secret = "test-secret"
    client = _build_client(secret)
    payload = {"hello": "world"}
    body = json.dumps(payload).encode("utf-8")
    timestamp = str(int(time.time()))
    signature = _sign_request(timestamp, "POST", "/protected", body, secret)

    response = client.post(
        "/protected",
        content=body,
        headers={
            "X-Timestamp": timestamp,
            "X-Signature": signature,
            "Content-Type": "application/json",
        },
    )

    assert response.status_code == 200
    assert response.json()["payload"] == payload


def test_hmac_invalid_signature() -> None:
    secret = "test-secret"
    client = _build_client(secret)
    payload = {"hello": "world"}
    body = json.dumps(payload).encode("utf-8")
    timestamp = str(int(time.time()))

    response = client.post(
        "/protected",
        content=body,
        headers={
            "X-Timestamp": timestamp,
            "X-Signature": "bad-signature",
            "Content-Type": "application/json",
        },
    )

    assert response.status_code == 401


def test_hmac_missing_headers() -> None:
    secret = "test-secret"
    client = _build_client(secret)
    payload = {"hello": "world"}

    response = client.post("/protected", json=payload)

    assert response.status_code == 401


def test_hmac_timestamp_outside_skew() -> None:
    secret = "test-secret"
    client = _build_client(secret)
    payload = {"hello": "world"}
    body = json.dumps(payload).encode("utf-8")
    timestamp = str(int(time.time()) - 1000)
    signature = _sign_request(timestamp, "POST", "/protected", body, secret)

    response = client.post(
        "/protected",
        content=body,
        headers={
            "X-Timestamp": timestamp,
            "X-Signature": signature,
            "Content-Type": "application/json",
        },
    )

    assert response.status_code == 401


def test_health_bypass() -> None:
    secret = "test-secret"
    client = _build_client(secret)

    response = client.get("/health")

    assert response.status_code == 200
