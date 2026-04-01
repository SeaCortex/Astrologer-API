from __future__ import annotations

from datetime import datetime, timedelta, timezone

from fastapi.testclient import TestClient

REFERENCE_2026_SOURCE_URL = "https://www.astropixels.com/almanac/almanac21/almanac2026gmt.html"
# UTC eclipse maxima extracted from the source above (accessed 2026-04-01), section:
# "2026 Astronomical Events (UT/GMT)".
REFERENCE_2026_ECLIPSES_UTC: list[tuple[str, str, str]] = [
    ("solar_eclipse", "annular", "2026-02-17T12:12:00+00:00"),
    ("lunar_eclipse", "total", "2026-03-03T11:34:00+00:00"),
    ("solar_eclipse", "total", "2026-08-12T17:46:00+00:00"),
    ("lunar_eclipse", "partial", "2026-08-28T04:13:00+00:00"),
]


def test_eclipse_events_returns_sorted_events_with_expected_shape(client: TestClient):
    payload = {
        "from_iso": "2026-01-01T00:00:00+00:00",
        "horizon_days": 365,
    }

    response = client.post("/api/v5/events/eclipses", json=payload)
    assert response.status_code == 200

    body = response.json()
    assert body["status"] == "OK"
    assert body["from_iso"] == "2026-01-01T00:00:00+00:00"
    assert body["horizon_days"] == 365
    assert body["event_types"] == ["solar", "lunar"]
    assert body["solar_types"] == ["total", "annular", "partial", "annular_total"]
    assert body["lunar_types"] == ["total", "partial", "penumbral"]

    events = body["events"]
    assert events, "Expected at least one eclipse event in this window."

    from_dt = datetime.fromisoformat(body["from_iso"]).astimezone(timezone.utc)
    horizon_dt = from_dt + timedelta(days=body["horizon_days"])

    previous_dt: datetime | None = None
    for item in events:
        assert item["event"] in {"solar_eclipse", "lunar_eclipse"}
        assert item["eclipse_type"] in {"total", "annular", "partial", "annular_total", "penumbral"}

        at_dt = datetime.fromisoformat(item["at_utc"]).astimezone(timezone.utc)
        assert from_dt <= at_dt <= horizon_dt
        if previous_dt is not None:
            assert at_dt >= previous_dt
        previous_dt = at_dt


def test_eclipse_events_defaults_from_iso_to_current_utc(client: TestClient):
    response = client.post("/api/v5/events/eclipses", json={"horizon_days": 30})
    assert response.status_code == 200

    body = response.json()
    assert body["status"] == "OK"
    assert body["horizon_days"] == 30
    assert isinstance(body["events"], list)

    from_dt = datetime.fromisoformat(body["from_iso"])
    assert from_dt.tzinfo is not None
    assert from_dt.utcoffset() == timedelta(0)


def test_eclipse_events_rejects_from_iso_without_timezone(client: TestClient):
    payload = {
        "from_iso": "2026-01-01T00:00:00",
        "horizon_days": 30,
    }
    response = client.post("/api/v5/events/eclipses", json=payload)
    assert response.status_code == 422


def test_eclipse_events_enforces_horizon_cap(client: TestClient):
    payload = {
        "horizon_days": 3651,
    }
    response = client.post("/api/v5/events/eclipses", json=payload)
    assert response.status_code == 422


def test_eclipse_events_normalizes_and_deduplicates_filters(client: TestClient):
    payload = {
        "from_iso": "2026-01-01T00:00:00+00:00",
        "horizon_days": 365,
        "event_types": ["SOLAR", "solar"],
        "solar_types": ["TOTAL", "total", "partial"],
    }

    response = client.post("/api/v5/events/eclipses", json=payload)
    assert response.status_code == 200

    body = response.json()
    assert body["event_types"] == ["solar"]
    assert body["solar_types"] == ["total", "partial"]
    assert all(item["event"] == "solar_eclipse" for item in body["events"])
    assert all(item["eclipse_type"] in {"total", "partial"} for item in body["events"])


def test_eclipse_events_can_filter_only_lunar_total(client: TestClient):
    payload = {
        "from_iso": "2026-01-01T00:00:00+00:00",
        "horizon_days": 365,
        "event_types": ["lunar"],
        "lunar_types": ["total"],
    }

    response = client.post("/api/v5/events/eclipses", json=payload)
    assert response.status_code == 200

    events = response.json()["events"]
    assert events
    assert all(item["event"] == "lunar_eclipse" for item in events)
    assert all(item["eclipse_type"] == "total" for item in events)


def test_eclipse_events_2026_match_reference_utc_times(client: TestClient):
    """
    Compares computed 2026 eclipse maxima with online UTC reference:
    https://www.astropixels.com/almanac/almanac21/almanac2026gmt.html
    """
    assert REFERENCE_2026_SOURCE_URL.startswith("https://")

    response = client.post(
        "/api/v5/events/eclipses",
        json={
            "from_iso": "2026-01-01T00:00:00+00:00",
            "horizon_days": 365,
        },
    )
    assert response.status_code == 200

    events = response.json()["events"]
    assert len(events) == len(REFERENCE_2026_ECLIPSES_UTC)

    for computed, (expected_event, expected_type, expected_iso) in zip(events, REFERENCE_2026_ECLIPSES_UTC, strict=True):
        assert computed["event"] == expected_event
        assert computed["eclipse_type"] == expected_type

        computed_dt = datetime.fromisoformat(computed["at_utc"]).astimezone(timezone.utc)
        expected_dt = datetime.fromisoformat(expected_iso).astimezone(timezone.utc)
        # Reference source provides minute precision; use conservative tolerance.
        assert abs((computed_dt - expected_dt).total_seconds()) <= 300
