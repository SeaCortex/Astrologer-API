from __future__ import annotations

from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo

from fastapi.testclient import TestClient
import pytest

REFERENCE_2026_ASPECTS_SOURCE_URL = "https://cafeastrology.com/2026-astrological-aspects.html"
# Source times below are published in Eastern Time (EST/EDT) and converted to UTC in tests.
# Extracted from source on 2026-04-01.
REFERENCE_2026_SELECTED_ASPECTS_ET = [
    # Feb 5, 2026 7:13 AM Mercury square Uranus
    {"planet_1": "Mercury", "planet_2": "Uranus", "aspect": "square", "pair_type": "rapid_slow", "at_et": "2026-02-05 07:13"},
    # Mar 18, 2026 12:09 PM Venus square Jupiter
    {"planet_1": "Venus", "planet_2": "Jupiter", "aspect": "square", "pair_type": "rapid_slow", "at_et": "2026-03-18 12:09"},
    # Apr 3, 2026 6:38 PM Venus square Pluto
    {"planet_1": "Venus", "planet_2": "Pluto", "aspect": "square", "pair_type": "rapid_slow", "at_et": "2026-04-03 18:38"},
    # Jun 17, 2026 4:38 PM Venus opposition Pluto
    {"planet_1": "Venus", "planet_2": "Pluto", "aspect": "opposition", "pair_type": "rapid_slow", "at_et": "2026-06-17 16:38"},
    # Jul 20, 2026 10:44 AM Jupiter opposition Pluto
    {"planet_1": "Jupiter", "planet_2": "Pluto", "aspect": "opposition", "pair_type": "slow_slow", "at_et": "2026-07-20 10:44"},
    # Jul 27, 2026 2:55 AM Sun opposition Pluto
    {"planet_1": "Sun", "planet_2": "Pluto", "aspect": "opposition", "pair_type": "rapid_slow", "at_et": "2026-07-27 02:55"},
]
REFERENCE_TIME_TOLERANCE_SECONDS = 15 * 60


def _et_to_utc_iso(et_timestamp: str) -> str:
    dt_et = datetime.strptime(et_timestamp, "%Y-%m-%d %H:%M").replace(tzinfo=ZoneInfo("America/New_York"))
    return dt_et.astimezone(timezone.utc).isoformat()


def test_aspect_events_returns_sorted_events_with_expected_shape(client: TestClient):
    payload = {
        "from_iso": "2026-03-01T00:00:00+00:00",
        "horizon_days": 40,
        "planets": ["Sun", "Moon"],
        "pair_types": ["rapid_rapid"],
        "aspect_types": ["square", "opposition"],
    }

    response = client.post("/api/v5/events/aspects", json=payload)
    assert response.status_code == 200

    body = response.json()
    assert body["status"] == "OK"
    assert body["from_iso"] == "2026-03-01T00:00:00+00:00"
    assert body["horizon_days"] == 40
    assert body["planets"] == ["Sun", "Moon"]
    assert body["pair_types"] == ["rapid_rapid"]
    assert body["aspect_types"] == ["square", "opposition"]

    events = body["events"]
    assert events, "Expected at least one Sun-Moon square/opposition event in a 40-day window."

    from_dt = datetime.fromisoformat(body["from_iso"]).astimezone(timezone.utc)
    horizon_dt = from_dt + timedelta(days=body["horizon_days"])

    previous_dt: datetime | None = None
    for item in events:
        assert item["event"] == "planetary_aspect"
        assert item["aspect"] in {"square", "opposition"}
        assert item["planet_1"] == "Sun"
        assert item["planet_2"] == "Moon"
        assert item["pair_type"] == "rapid_rapid"
        assert item["orbit_deg"] >= 0
        assert item["orbit_deg"] <= 0.05
        assert isinstance(item["p1_speed"], float)
        assert isinstance(item["p2_speed"], float)

        target_angle = item["target_angle_deg"]
        if item["aspect"] == "square":
            assert target_angle in {90.0, 270.0}
        else:
            assert target_angle == 180.0

        at_dt = datetime.fromisoformat(item["at_utc"]).astimezone(timezone.utc)
        assert from_dt <= at_dt <= horizon_dt
        if previous_dt is not None:
            assert at_dt >= previous_dt
        previous_dt = at_dt


def test_aspect_events_defaults_from_iso_planets_pair_types_and_aspect_types(client: TestClient):
    response = client.post("/api/v5/events/aspects", json={"horizon_days": 5})
    assert response.status_code == 200

    body = response.json()
    assert body["status"] == "OK"
    assert body["horizon_days"] == 5
    assert body["planets"] == ["Sun", "Mercury", "Venus", "Mars", "Jupiter", "Saturn", "Uranus", "Neptune", "Pluto"]
    assert body["pair_types"] == ["rapid_slow", "slow_slow"]
    assert body["aspect_types"] == ["square", "opposition"]
    assert isinstance(body["events"], list)

    from_dt = datetime.fromisoformat(body["from_iso"])
    assert from_dt.tzinfo is not None
    assert from_dt.utcoffset() == timedelta(0)


def test_aspect_events_rejects_from_iso_without_timezone(client: TestClient):
    payload = {
        "from_iso": "2026-03-01T00:00:00",
        "horizon_days": 30,
    }
    response = client.post("/api/v5/events/aspects", json=payload)
    assert response.status_code == 422


def test_aspect_events_enforces_horizon_cap(client: TestClient):
    payload = {"horizon_days": 3651}
    response = client.post("/api/v5/events/aspects", json=payload)
    assert response.status_code == 422


def test_aspect_events_normalizes_and_deduplicates_inputs(client: TestClient):
    payload = {
        "from_iso": "2026-03-01T00:00:00+00:00",
        "horizon_days": 20,
        "planets": ["moon", "MOON", "sun"],
        "pair_types": ["RAPID_RAPID", "rapid_rapid"],
        "aspect_types": ["SQUARE", "square", "OPPOSITION"],
    }

    response = client.post("/api/v5/events/aspects", json=payload)
    assert response.status_code == 200

    body = response.json()
    assert body["planets"] == ["Moon", "Sun"]
    assert body["pair_types"] == ["rapid_rapid"]
    assert body["aspect_types"] == ["square", "opposition"]
    assert all({event["planet_1"], event["planet_2"]} == {"Sun", "Moon"} for event in body["events"])
    assert all(event["aspect"] in {"square", "opposition"} for event in body["events"])


def test_aspect_events_rejects_invalid_planets(client: TestClient):
    payload = {
        "horizon_days": 30,
        "planets": ["Sun", "Chiron"],
    }
    response = client.post("/api/v5/events/aspects", json=payload)
    assert response.status_code == 422


def test_aspect_events_rejects_invalid_aspect_types(client: TestClient):
    payload = {
        "horizon_days": 30,
        "aspect_types": ["trine"],
    }
    response = client.post("/api/v5/events/aspects", json=payload)
    assert response.status_code == 422


def test_aspect_events_returns_empty_when_pair_type_excludes_all_pairs(client: TestClient):
    payload = {
        "from_iso": "2026-03-01T00:00:00+00:00",
        "horizon_days": 30,
        "planets": ["Sun", "Jupiter"],
        "pair_types": ["slow_slow"],
        "aspect_types": ["square", "opposition"],
    }
    response = client.post("/api/v5/events/aspects", json=payload)
    assert response.status_code == 200

    body = response.json()
    assert body["events"] == []


@pytest.mark.parametrize("reference", REFERENCE_2026_SELECTED_ASPECTS_ET)
def test_aspect_events_2026_selected_pairs_match_online_reference(client: TestClient, reference: dict):
    """
    Compares selected 2026 square/opposition instants with online ET reference:
    https://cafeastrology.com/2026-astrological-aspects.html
    """
    assert REFERENCE_2026_ASPECTS_SOURCE_URL.startswith("https://")

    expected_dt = datetime.fromisoformat(_et_to_utc_iso(reference["at_et"])).astimezone(timezone.utc)
    from_dt = expected_dt - timedelta(days=3)

    response = client.post(
        "/api/v5/events/aspects",
        json={
            "from_iso": from_dt.isoformat(),
            "horizon_days": 7,
            "planets": [reference["planet_1"], reference["planet_2"]],
            "pair_types": [reference["pair_type"]],
            "aspect_types": [reference["aspect"]],
        },
    )
    assert response.status_code == 200

    events = response.json()["events"]
    assert len(events) == 1

    computed = events[0]
    assert computed["event"] == "planetary_aspect"
    assert computed["planet_1"] == reference["planet_1"]
    assert computed["planet_2"] == reference["planet_2"]
    assert computed["pair_type"] == reference["pair_type"]
    assert computed["aspect"] == reference["aspect"]
    if reference["aspect"] == "square":
        assert computed["target_angle_deg"] in {90.0, 270.0}
    else:
        assert computed["target_angle_deg"] == 180.0

    computed_dt = datetime.fromisoformat(computed["at_utc"]).astimezone(timezone.utc)
    assert abs((computed_dt - expected_dt).total_seconds()) <= REFERENCE_TIME_TOLERANCE_SECONDS
