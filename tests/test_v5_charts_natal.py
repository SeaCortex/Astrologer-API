"""
Test espliciti per gli endpoint natal: chart-data e charts.

Obiettivi minimi e chiari:
- Le chiamate rispondono 200.
- La chart SVG è presente.
- La struttura `chart_data` è coerente con un grafico singolo.
"""

from __future__ import annotations

from copy import deepcopy
from typing import Dict

from fastapi.testclient import TestClient


BASE_SUBJECT: Dict[str, object] = {
    "name": "FastAPI Unit Test",
    "year": 1980,
    "month": 12,
    "day": 12,
    "hour": 12,
    "minute": 12,
    "longitude": 0,
    "latitude": 51.4825766,
    "city": "London",
    "nation": "GB",
    "timezone": "Europe/London",
}


def test_natal_chart_data(client: TestClient):
    resp = client.post("/api/v5/chart-data/natal", json={"subject": deepcopy(BASE_SUBJECT)})
    assert resp.status_code == 200
    data = resp.json()["chart_data"]

    assert data["chart_type"] == "Natal"
    assert "subject" in data
    assert isinstance(data["active_points"], list) and data["active_points"]
    assert isinstance(data["active_aspects"], list) and data["active_aspects"]
    assert isinstance(data["aspects"], list)


def test_natal_chart_svg(client: TestClient):
    resp = client.post("/api/v5/charts/natal", json={"subject": deepcopy(BASE_SUBJECT)})
    assert resp.status_code == 200
    body = resp.json()

    # Chart SVG
    assert isinstance(body["chart"], str) and "<svg" in body["chart"]

    # Chart data coerenti
    data = body["chart_data"]
    assert data["chart_type"] == "Natal"
    assert "subject" in data

