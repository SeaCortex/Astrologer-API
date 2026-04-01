from __future__ import annotations

from datetime import datetime, timedelta, timezone

from fastapi.testclient import TestClient

REFERENCE_2026_SOURCE_URL = "https://cafeastrology.com/astrology-of-2026.html"
# Source table times are published in Eastern Time (EST/EDT). Converted to UTC below.
# Extracted from source on 2026-03-31.
REFERENCE_2026_SUN_INGRESSES_UTC: list[str] = [
    "2026-01-20T01:45:00+00:00",  # Jan 19 8:45 PM ET (EST)
    "2026-02-18T15:52:00+00:00",  # Feb 18 10:52 AM ET (EST)
    "2026-03-20T14:46:00+00:00",  # Mar 20 10:46 AM ET (EDT)
    "2026-04-20T01:39:00+00:00",  # Apr 19 9:39 PM ET (EDT)
    "2026-05-21T00:36:00+00:00",  # May 20 8:36 PM ET (EDT)
    "2026-06-21T08:24:00+00:00",  # Jun 21 4:24 AM ET (EDT)
    "2026-07-22T19:13:00+00:00",  # Jul 22 3:13 PM ET (EDT)
    "2026-08-23T02:19:00+00:00",  # Aug 22 10:19 PM ET (EDT)
    "2026-09-23T00:05:00+00:00",  # Sep 22 8:05 PM ET (EDT)
    "2026-10-23T09:38:00+00:00",  # Oct 23 5:38 AM ET (EDT)
    "2026-11-22T07:23:00+00:00",  # Nov 22 2:23 AM ET (EST)
    "2026-12-21T20:50:00+00:00",  # Dec 21 3:50 PM ET (EST)
]

REFERENCE_2026_MAJOR_INGRESSES_UTC: dict[str, str] = {
    "Neptune": "2026-01-26T17:34:00+00:00",  # Jan 26 12:34 PM ET (EST)
    "Saturn": "2026-02-14T00:11:00+00:00",   # Feb 13 7:11 PM ET (EST)
    "Uranus": "2026-04-26T00:51:00+00:00",   # Apr 25 8:51 PM ET (EDT)
    "Jupiter": "2026-06-30T05:52:00+00:00",  # Jun 30 1:52 AM ET (EDT)
}


def test_ingress_events_returns_sorted_events_with_expected_shape(client: TestClient):
    payload = {
        "from_iso": "2026-03-01T00:00:00+00:00",
        "horizon_days": 10,
        "planets": ["Moon"],
    }

    response = client.post("/api/v5/events/ingress", json=payload)
    assert response.status_code == 200

    body = response.json()
    assert body["status"] == "OK"
    assert body["from_iso"] == "2026-03-01T00:00:00+00:00"
    assert body["horizon_days"] == 10
    assert body["planets"] == ["Moon"]

    events = body["events"]
    assert events, "Expected at least one Moon sign ingress in a 10-day window."

    from_dt = datetime.fromisoformat(body["from_iso"]).astimezone(timezone.utc)
    horizon_dt = from_dt + timedelta(days=body["horizon_days"])

    previous_dt: datetime | None = None
    for item in events:
        assert item["event"] == "sign_ingress"
        assert item["planet"] == "Moon"
        assert item["from_sign"] != item["to_sign"]

        at_dt = datetime.fromisoformat(item["at_utc"]).astimezone(timezone.utc)
        assert from_dt <= at_dt <= horizon_dt
        if previous_dt is not None:
            assert at_dt >= previous_dt
        previous_dt = at_dt


def test_ingress_events_defaults_from_iso_and_planets(client: TestClient):
    response = client.post("/api/v5/events/ingress", json={"horizon_days": 2})
    assert response.status_code == 200

    body = response.json()
    assert body["status"] == "OK"
    assert body["horizon_days"] == 2
    assert isinstance(body["events"], list)
    assert body["planets"] == [
        "Sun",
        "Moon",
        "Mercury",
        "Venus",
        "Mars",
        "Jupiter",
        "Saturn",
        "Uranus",
        "Neptune",
        "Pluto",
    ]

    from_dt = datetime.fromisoformat(body["from_iso"])
    assert from_dt.tzinfo is not None
    assert from_dt.utcoffset() == timedelta(0)


def test_ingress_events_rejects_from_iso_without_timezone(client: TestClient):
    payload = {
        "from_iso": "2026-03-01T00:00:00",
        "horizon_days": 30,
    }
    response = client.post("/api/v5/events/ingress", json=payload)
    assert response.status_code == 422


def test_ingress_events_enforces_horizon_cap(client: TestClient):
    payload = {
        "horizon_days": 731,
    }
    response = client.post("/api/v5/events/ingress", json=payload)
    assert response.status_code == 422


def test_ingress_events_normalizes_and_deduplicates_planets(client: TestClient):
    payload = {
        "from_iso": "2026-03-01T00:00:00+00:00",
        "horizon_days": 10,
        "planets": ["moon", "MOON", "sun"],
    }

    response = client.post("/api/v5/events/ingress", json=payload)
    assert response.status_code == 200

    body = response.json()
    assert body["planets"] == ["Moon", "Sun"]
    assert all(item["planet"] in {"Moon", "Sun"} for item in body["events"])


def test_ingress_events_accepts_lilith_points(client: TestClient):
    payload = {
        "from_iso": "2026-03-01T00:00:00+00:00",
        "horizon_days": 30,
        "planets": ["mean_lilith", "TRUE_lilith"],
    }

    response = client.post("/api/v5/events/ingress", json=payload)
    assert response.status_code == 200

    body = response.json()
    assert body["planets"] == ["Mean_Lilith", "True_Lilith"]
    assert all(item["planet"] in {"Mean_Lilith", "True_Lilith"} for item in body["events"])


def test_ingress_events_rejects_invalid_planets(client: TestClient):
    payload = {
        "horizon_days": 30,
        "planets": ["Sun", "Chiron"],
    }
    response = client.post("/api/v5/events/ingress", json=payload)
    assert response.status_code == 422


def test_ingress_events_2026_sun_match_reference_utc_times(client: TestClient):
    """
    Compares computed Sun ingress instants for 2026 with an online reference table:
    https://cafeastrology.com/astrology-of-2026.html
    """
    assert REFERENCE_2026_SOURCE_URL.startswith("https://")

    response = client.post(
        "/api/v5/events/ingress",
        json={
            "from_iso": "2026-01-01T00:00:00+00:00",
            "horizon_days": 365,
            "planets": ["Sun"],
        },
    )
    assert response.status_code == 200

    events = response.json()["events"]
    assert len(events) == len(REFERENCE_2026_SUN_INGRESSES_UTC)

    for computed, expected_iso in zip(events, REFERENCE_2026_SUN_INGRESSES_UTC, strict=True):
        assert computed["event"] == "sign_ingress"
        assert computed["planet"] == "Sun"

        computed_dt = datetime.fromisoformat(computed["at_utc"]).astimezone(timezone.utc)
        expected_dt = datetime.fromisoformat(expected_iso).astimezone(timezone.utc)
        # Source table is minute-granular and ET-based; keep a conservative tolerance.
        assert abs((computed_dt - expected_dt).total_seconds()) <= 300


def test_ingress_events_2026_major_planet_ingresses_match_reference(client: TestClient):
    """
    Validates key 2026 sign ingresses for major planets against the same online reference.
    """
    response = client.post(
        "/api/v5/events/ingress",
        json={
            "from_iso": "2026-01-01T00:00:00+00:00",
            "horizon_days": 365,
            "planets": ["Neptune", "Saturn", "Uranus", "Jupiter"],
        },
    )
    assert response.status_code == 200

    events = response.json()["events"]
    by_planet = {item["planet"]: item for item in events}
    assert set(by_planet.keys()) == set(REFERENCE_2026_MAJOR_INGRESSES_UTC.keys())

    for planet, expected_iso in REFERENCE_2026_MAJOR_INGRESSES_UTC.items():
        computed_dt = datetime.fromisoformat(by_planet[planet]["at_utc"]).astimezone(timezone.utc)
        expected_dt = datetime.fromisoformat(expected_iso).astimezone(timezone.utc)
        # Cross-source ingress references can differ by several minutes depending
        # on calculation method and rounding policy.
        assert abs((computed_dt - expected_dt).total_seconds()) <= 900
