from __future__ import annotations

from datetime import datetime, timezone

from fastapi.testclient import TestClient


def test_retrogrades_next_include_ongoing_true_returns_current_window(client: TestClient):
    payload = {
        "from_iso": "2024-08-10T00:00:00+00:00",
        "horizon_days": 60,
        "planets": ["Mercury"],
        "include_ongoing": True,
    }

    response = client.post("/api/v5/retrogrades/next", json=payload)
    assert response.status_code == 200

    body = response.json()
    assert body["status"] == "OK"
    assert body["from_iso"].startswith("2024-08-10T00:00:00+00:00")
    assert body["horizon_days"] == 60
    assert body["include_ongoing"] is True

    retrograde = body["retrogrades"][0]
    assert retrograde["planet"] == "Mercury"
    assert retrograde["is_ongoing"] is True
    assert retrograde["started_before_from"] is True
    assert retrograde["start_speed"] is not None and retrograde["start_speed"] < 0
    assert retrograde["next_end_utc"] is not None
    assert retrograde["end_speed"] is not None and retrograde["end_speed"] > 0


def test_retrogrades_next_include_ongoing_false_returns_strictly_future_window(client: TestClient):
    from_iso = "2024-08-10T00:00:00+00:00"
    payload = {
        "from_iso": from_iso,
        "horizon_days": 150,
        "planets": ["Mercury"],
        "include_ongoing": False,
    }

    response = client.post("/api/v5/retrogrades/next", json=payload)
    assert response.status_code == 200

    body = response.json()
    retrograde = body["retrogrades"][0]

    assert retrograde["planet"] == "Mercury"
    assert retrograde["is_ongoing"] is False
    assert retrograde["started_before_from"] is False
    assert retrograde["next_start_utc"] is not None
    assert retrograde["next_end_utc"] is not None
    assert retrograde["start_speed"] is not None and retrograde["start_speed"] < 0
    assert retrograde["end_speed"] is not None and retrograde["end_speed"] > 0

    start_dt = datetime.fromisoformat(retrograde["next_start_utc"]).astimezone(timezone.utc)
    from_dt = datetime.fromisoformat(from_iso).astimezone(timezone.utc)
    assert start_dt > from_dt


def test_retrogrades_next_normalizes_and_deduplicates_planets(client: TestClient):
    payload = {
        "from_iso": "2024-08-10T00:00:00+00:00",
        "horizon_days": 30,
        "planets": ["mercury", "MERCURY", "venus"],
    }

    response = client.post("/api/v5/retrogrades/next", json=payload)
    assert response.status_code == 200
    body = response.json()

    assert [item["planet"] for item in body["retrogrades"]] == ["Mercury", "Venus"]


def test_retrogrades_next_rejects_invalid_planets(client: TestClient):
    payload = {
        "horizon_days": 30,
        "planets": ["Mercury", "Sun"],
    }
    response = client.post("/api/v5/retrogrades/next", json=payload)
    assert response.status_code == 422


def test_retrogrades_next_enforces_horizon_cap(client: TestClient):
    payload = {
        "horizon_days": 731,
        "planets": ["Mercury"],
    }
    response = client.post("/api/v5/retrogrades/next", json=payload)
    assert response.status_code == 422
