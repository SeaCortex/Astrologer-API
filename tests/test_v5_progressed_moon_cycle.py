from __future__ import annotations

from copy import deepcopy
from typing import Dict

from fastapi.testclient import TestClient


BASE_SUBJECT: Dict[str, object] = {
    "name": "Progressed Moon Test",
    "year": 1990,
    "month": 5,
    "day": 1,
    "hour": 10,
    "minute": 0,
    "longitude": 12.4964,
    "latitude": 41.9028,
    "city": "Rome",
    "nation": "IT",
    "timezone": "Europe/Rome",
}


def test_progressed_moon_cycle_endpoint_returns_phase_and_ingresses(client: TestClient):
    payload = {
        "subject": deepcopy(BASE_SUBJECT),
        "target_iso_datetime": "2026-02-12T00:00:00+00:00",
        "range_end_iso_datetime": "2029-02-12T00:00:00+00:00",
        "step_days": 21,
    }
    response = client.post("/api/v5/chart-data/progressed-moon-cycle", json=payload)
    assert response.status_code == 200

    body = response.json()
    assert body["status"] == "OK"
    cycle = body["progressed_moon_cycle"]

    assert "progressed_iso_datetime" in cycle
    assert "progressed_subject" in cycle

    lunation = cycle["progressed_lunation"]
    assert 0.0 <= lunation["angle_deg"] < 360.0
    assert lunation["phase_name"] in {"New Moon", "First Quarter", "Full Moon", "Last Quarter"}

    # Over a 3-year range a secondary progressed Moon should always ingress sign at least once.
    assert cycle["next_ingresses"]["next_sign_ingress"] is not None


def test_progressed_moon_cycle_range_validation(client: TestClient):
    payload = {
        "subject": deepcopy(BASE_SUBJECT),
        "target_iso_datetime": "2026-02-12T00:00:00+00:00",
        "range_end_iso_datetime": "2025-02-12T00:00:00+00:00",
    }
    response = client.post("/api/v5/chart-data/progressed-moon-cycle", json=payload)
    assert response.status_code == 422
