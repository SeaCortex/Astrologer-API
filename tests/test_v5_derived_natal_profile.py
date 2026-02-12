from __future__ import annotations

from copy import deepcopy
from typing import Dict

from fastapi.testclient import TestClient


BASE_SUBJECT: Dict[str, object] = {
    "name": "Derived Endpoint Test",
    "year": 1990,
    "month": 6,
    "day": 15,
    "hour": 12,
    "minute": 30,
    "longitude": 12.4964,
    "latitude": 41.9028,
    "city": "Rome",
    "nation": "IT",
    "timezone": "Europe/Rome",
}


def test_derived_natal_profile_endpoint_returns_expected_shape(client: TestClient):
    response = client.post("/api/v5/derived/natal-profile", json={"subject": deepcopy(BASE_SUBJECT)})
    assert response.status_code == 200

    payload = response.json()
    assert payload["status"] == "OK"
    assert "subject" in payload
    assert "derived_profile" in payload

    derived = payload["derived_profile"]
    assert "chart_ruler" in derived
    assert "stelliums" in derived
    assert "hemispheres" in derived
    assert "lunar_mansion" in derived

    assert derived["lunar_mansion"]["system"] == "tropical_28_equal"
    assert 1 <= derived["lunar_mansion"]["index"] <= 28


def test_derived_natal_profile_respects_active_points_filtering(client: TestClient):
    response = client.post(
        "/api/v5/derived/natal-profile",
        json={
            "subject": deepcopy(BASE_SUBJECT),
            "active_points": ["Sun", "Moon"],
        },
    )
    assert response.status_code == 200
    payload = response.json()
    derived = payload["derived_profile"]

    assert derived["stelliums"]["by_sign"] == []
    assert derived["stelliums"]["by_house"] == []
    assert len(derived["hemispheres"]["above_below_horizon"]["counted_points"]) <= 2
