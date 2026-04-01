from __future__ import annotations

from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo

from fastapi.testclient import TestClient
import pytest

REFERENCE_2026_CONJUNCTIONS_SOURCE_URL = "https://cafeastrology.com/2026-astrological-aspects.html"
# Source times below are published in Eastern Time (EST/EDT) and converted to UTC in tests.
# Extracted from source on 2026-04-01.
REFERENCE_2026_SELECTED_CONJUNCTIONS_ET = [
    # Feb 20, 2026 11:54 AM  Saturn conjunction Neptune
    {"planet_1": "Saturn", "planet_2": "Neptune", "pair_type": "slow_slow", "at_et": "2026-02-20 11:54"},
    # Feb 28, 2026 12:35 AM  Mercury conjunction Venus
    {"planet_1": "Mercury", "planet_2": "Venus", "pair_type": "rapid_rapid", "at_et": "2026-02-28 00:35"},
    # Mar 7, 2026 6:01 AM  Sun conjunction Mercury
    {"planet_1": "Sun", "planet_2": "Mercury", "pair_type": "rapid_rapid", "at_et": "2026-03-07 06:01"},
    # Mar 7, 2026 6:27 AM  Venus conjunction Neptune
    {"planet_1": "Venus", "planet_2": "Neptune", "pair_type": "rapid_slow", "at_et": "2026-03-07 06:27"},
    # Mar 8, 2026 9:39 AM  Venus conjunction Saturn
    {"planet_1": "Venus", "planet_2": "Saturn", "pair_type": "rapid_slow", "at_et": "2026-03-08 09:39"},
    # Mar 15, 2026 4:08 AM  Mercury conjunction Mars
    {"planet_1": "Mercury", "planet_2": "Mars", "pair_type": "rapid_rapid", "at_et": "2026-03-15 04:08"},
]
REFERENCE_TIME_TOLERANCE_SECONDS = 15 * 60


def _et_to_utc_iso(et_timestamp: str) -> str:
    # Source table is Eastern Time with DST rules; convert to UTC for assertions.
    dt_et = datetime.strptime(et_timestamp, "%Y-%m-%d %H:%M").replace(tzinfo=ZoneInfo("America/New_York"))
    return dt_et.astimezone(timezone.utc).isoformat()


def test_conjunction_events_returns_sorted_events_with_expected_shape(client: TestClient):
    payload = {
        "from_iso": "2026-03-01T00:00:00+00:00",
        "horizon_days": 40,
        "planets": ["Sun", "Moon"],
        "pair_types": ["rapid_rapid"],
    }

    response = client.post("/api/v5/events/conjunctions", json=payload)
    assert response.status_code == 200

    body = response.json()
    assert body["status"] == "OK"
    assert body["from_iso"] == "2026-03-01T00:00:00+00:00"
    assert body["horizon_days"] == 40
    assert body["planets"] == ["Sun", "Moon"]
    assert body["pair_types"] == ["rapid_rapid"]

    events = body["events"]
    assert events, "Expected at least one Sun-Moon conjunction in a 40-day window."

    from_dt = datetime.fromisoformat(body["from_iso"]).astimezone(timezone.utc)
    horizon_dt = from_dt + timedelta(days=body["horizon_days"])

    previous_dt: datetime | None = None
    for item in events:
        assert item["event"] == "planetary_conjunction"
        assert item["planet_1"] == "Sun"
        assert item["planet_2"] == "Moon"
        assert item["pair_type"] == "rapid_rapid"
        assert item["orbit_deg"] >= 0
        assert item["orbit_deg"] <= 0.05
        assert isinstance(item["p1_speed"], float)
        assert isinstance(item["p2_speed"], float)

        at_dt = datetime.fromisoformat(item["at_utc"]).astimezone(timezone.utc)
        assert from_dt <= at_dt <= horizon_dt
        if previous_dt is not None:
            assert at_dt >= previous_dt
        previous_dt = at_dt


def test_conjunction_events_defaults_from_iso_planets_and_pair_types(client: TestClient):
    response = client.post("/api/v5/events/conjunctions", json={"horizon_days": 5})
    assert response.status_code == 200

    body = response.json()
    assert body["status"] == "OK"
    assert body["horizon_days"] == 5
    assert body["planets"] == ["Sun", "Mercury", "Venus", "Mars", "Jupiter", "Saturn", "Uranus", "Neptune", "Pluto"]
    assert body["pair_types"] == ["rapid_slow", "slow_slow"]
    assert isinstance(body["events"], list)

    from_dt = datetime.fromisoformat(body["from_iso"])
    assert from_dt.tzinfo is not None
    assert from_dt.utcoffset() == timedelta(0)


def test_conjunction_events_rejects_from_iso_without_timezone(client: TestClient):
    payload = {
        "from_iso": "2026-03-01T00:00:00",
        "horizon_days": 30,
    }
    response = client.post("/api/v5/events/conjunctions", json=payload)
    assert response.status_code == 422


def test_conjunction_events_enforces_horizon_cap(client: TestClient):
    payload = {"horizon_days": 3651}
    response = client.post("/api/v5/events/conjunctions", json=payload)
    assert response.status_code == 422


def test_conjunction_events_normalizes_and_deduplicates_inputs(client: TestClient):
    payload = {
        "from_iso": "2026-03-01T00:00:00+00:00",
        "horizon_days": 40,
        "planets": ["moon", "MOON", "sun"],
        "pair_types": ["RAPID_RAPID", "rapid_rapid"],
    }

    response = client.post("/api/v5/events/conjunctions", json=payload)
    assert response.status_code == 200

    body = response.json()
    assert body["planets"] == ["Moon", "Sun"]
    assert body["pair_types"] == ["rapid_rapid"]
    assert all({event["planet_1"], event["planet_2"]} == {"Sun", "Moon"} for event in body["events"])


def test_conjunction_events_rejects_invalid_planets(client: TestClient):
    payload = {
        "horizon_days": 30,
        "planets": ["Sun", "Chiron"],
    }
    response = client.post("/api/v5/events/conjunctions", json=payload)
    assert response.status_code == 422


def test_conjunction_events_returns_empty_when_pair_type_excludes_all_pairs(client: TestClient):
    payload = {
        "from_iso": "2026-03-01T00:00:00+00:00",
        "horizon_days": 30,
        "planets": ["Sun", "Jupiter"],
        "pair_types": ["slow_slow"],
    }
    response = client.post("/api/v5/events/conjunctions", json=payload)
    assert response.status_code == 200

    body = response.json()
    assert body["events"] == []


@pytest.mark.parametrize("reference", REFERENCE_2026_SELECTED_CONJUNCTIONS_ET)
def test_conjunction_events_2026_selected_pairs_match_online_reference(client: TestClient, reference: dict):
    """
    Compares selected 2026 conjunction instants with online ET reference:
    https://cafeastrology.com/2026-astrological-aspects.html
    """
    assert REFERENCE_2026_CONJUNCTIONS_SOURCE_URL.startswith("https://")

    expected_dt = datetime.fromisoformat(_et_to_utc_iso(reference["at_et"])).astimezone(timezone.utc)
    from_dt = expected_dt - timedelta(days=3)

    response = client.post(
        "/api/v5/events/conjunctions",
        json={
            "from_iso": from_dt.isoformat(),
            "horizon_days": 7,
            "planets": [reference["planet_1"], reference["planet_2"]],
            "pair_types": [reference["pair_type"]],
        },
    )
    assert response.status_code == 200

    events = response.json()["events"]
    assert len(events) == 1

    computed = events[0]
    assert computed["event"] == "planetary_conjunction"
    assert computed["planet_1"] == reference["planet_1"]
    assert computed["planet_2"] == reference["planet_2"]
    assert computed["pair_type"] == reference["pair_type"]

    computed_dt = datetime.fromisoformat(computed["at_utc"]).astimezone(timezone.utc)
    assert abs((computed_dt - expected_dt).total_seconds()) <= REFERENCE_TIME_TOLERANCE_SECONDS
