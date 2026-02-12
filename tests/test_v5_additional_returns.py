from __future__ import annotations

from copy import deepcopy
from typing import Dict

from fastapi.testclient import TestClient


BASE_SUBJECT: Dict[str, object] = {
    "name": "Additional Return Test",
    "year": 1995,
    "month": 7,
    "day": 14,
    "hour": 9,
    "minute": 20,
    "longitude": -0.1276,
    "latitude": 51.5074,
    "city": "London",
    "nation": "GB",
    "timezone": "Europe/London",
}


def _circular_diff(a: float, b: float) -> float:
    diff = abs(a - b)
    if diff > 180:
        diff = 360 - diff
    return diff


def _natal_point_abs_pos(client: TestClient, point_key: str) -> float:
    payload = {
        "subject": deepcopy(BASE_SUBJECT),
        "active_points": ["Sun", "Moon", "Jupiter", "Saturn", "Mean_North_Lunar_Node", "Ascendant"],
    }
    response = client.post("/api/v5/subject", json=payload)
    assert response.status_code == 200
    return float(response.json()["subject"][point_key]["abs_pos"])


def test_saturn_return_data_single_wheel_matches_natal_saturn(client: TestClient):
    natal_saturn = _natal_point_abs_pos(client, "saturn")

    response = client.post(
        "/api/v5/chart-data/saturn-return",
        json={"subject": deepcopy(BASE_SUBJECT), "year": 2024, "wheel_type": "single"},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["return_type"] == "Saturn"
    assert body["wheel_type"] == "single"
    assert body["chart_data"]["chart_type"] == "SingleReturnChart"

    return_saturn = float(body["chart_data"]["subject"]["saturn"]["abs_pos"])
    assert _circular_diff(return_saturn, natal_saturn) < 0.1


def test_jupiter_return_data_single_wheel_matches_natal_jupiter(client: TestClient):
    natal_jupiter = _natal_point_abs_pos(client, "jupiter")

    response = client.post(
        "/api/v5/chart-data/jupiter-return",
        json={"subject": deepcopy(BASE_SUBJECT), "year": 2024, "wheel_type": "single"},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["return_type"] == "Jupiter"
    assert body["wheel_type"] == "single"
    assert body["chart_data"]["chart_type"] == "SingleReturnChart"

    return_jupiter = float(body["chart_data"]["subject"]["jupiter"]["abs_pos"])
    assert _circular_diff(return_jupiter, natal_jupiter) < 0.1


def test_mean_node_return_data_single_wheel_matches_natal_mean_node(client: TestClient):
    natal_mean_node = _natal_point_abs_pos(client, "mean_north_lunar_node")

    response = client.post(
        "/api/v5/chart-data/lunar-node-return",
        json={"subject": deepcopy(BASE_SUBJECT), "year": 2024, "wheel_type": "single"},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["return_type"] == "MeanNode"
    assert body["wheel_type"] == "single"
    assert body["chart_data"]["chart_type"] == "SingleReturnChart"

    return_mean_node = float(body["chart_data"]["subject"]["mean_north_lunar_node"]["abs_pos"])
    assert _circular_diff(return_mean_node, natal_mean_node) < 0.1


def test_saturn_return_dual_wheel_has_natal_and_return_subjects(client: TestClient):
    response = client.post(
        "/api/v5/chart-data/saturn-return",
        json={"subject": deepcopy(BASE_SUBJECT), "year": 2024, "wheel_type": "dual"},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["return_type"] == "Saturn"
    assert body["wheel_type"] == "dual"
    assert body["chart_data"]["chart_type"] == "DualReturnChart"
    assert body["chart_data"]["second_subject"]["return_type"] == "Saturn"
