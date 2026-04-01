from __future__ import annotations

from datetime import datetime, timedelta, timezone

from fastapi.testclient import TestClient

REFERENCE_2026_SOURCE_URL = "https://www.astrosynthesis.com.au/wp-content/uploads/2025/12/2026-Retrogrades.pdf"
# UT station dates extracted from the online reference above (accessed 2026-03-31).
# Expected format per planet: list of (retrograde_start_date, direct_station_date).
REFERENCE_2026_WINDOWS_UT: dict[str, list[tuple[str, str]]] = {
    "Mercury": [("2026-02-26", "2026-03-20"), ("2026-06-29", "2026-07-23"), ("2026-10-24", "2026-11-13")],
    "Venus": [("2026-10-03", "2026-11-14")],
    "Mars": [],
    "Jupiter": [("2026-12-13", "2027-04-13")],
    "Saturn": [("2026-07-26", "2026-12-10")],
    "Uranus": [("2026-09-10", "2027-02-08")],
    "Neptune": [("2026-07-07", "2026-12-12")],
    "Pluto": [("2026-05-06", "2026-10-16")],
}


def _get_windows_starting_in_year(client: TestClient, planet: str, year: int) -> list[tuple[str, str]]:
    response = client.post(
        "/api/v5/events/retrogrades",
        json={
            "from_iso": datetime(year, 1, 1, tzinfo=timezone.utc).isoformat(),
            "horizon_days": 500,
            "planets": [planet],
        },
    )
    assert response.status_code == 200

    windows: list[tuple[str, str]] = []
    for event in response.json()["events"]:
        if event["planet"] != planet:
            continue

        start_dt = datetime.fromisoformat(event["at_utc"]).astimezone(timezone.utc)
        if start_dt.year != year:
            continue

        end_iso = event["ends_at_utc"]
        assert end_iso is not None
        end_dt = datetime.fromisoformat(end_iso).astimezone(timezone.utc)
        windows.append((start_dt.date().isoformat(), end_dt.date().isoformat()))

    return windows


def test_retrograde_events_returns_sorted_events_with_expected_shape(client: TestClient):
    payload = {
        "from_iso": "2026-01-01T00:00:00+00:00",
        "horizon_days": 365,
        "planets": ["Mercury", "Venus"],
    }

    response = client.post("/api/v5/events/retrogrades", json=payload)
    assert response.status_code == 200

    body = response.json()
    assert body["status"] == "OK"
    assert body["from_iso"].startswith("2026-01-01T00:00:00+00:00")
    assert body["horizon_days"] == 365
    assert body["planets"] == ["Mercury", "Venus"]
    assert isinstance(body["events"], list)

    from_dt = datetime.fromisoformat(body["from_iso"]).astimezone(timezone.utc)
    horizon_dt = from_dt + timedelta(days=body["horizon_days"])
    previous_dt: datetime | None = None

    for event in body["events"]:
        assert event["event"] == "retrograde_period"
        assert event["planet"] in {"Mercury", "Venus"}
        assert event["start_speed"] is not None and event["start_speed"] < 0

        at_dt = datetime.fromisoformat(event["at_utc"]).astimezone(timezone.utc)
        assert from_dt <= at_dt <= horizon_dt
        if previous_dt is not None:
            assert at_dt >= previous_dt
        previous_dt = at_dt

        if event["ends_at_utc"] is None:
            assert event["end_speed"] is None
            continue

        end_dt = datetime.fromisoformat(event["ends_at_utc"]).astimezone(timezone.utc)
        assert at_dt <= end_dt
        assert event["end_speed"] is not None and event["end_speed"] > 0


def test_retrograde_events_defaults_from_iso_and_planets(client: TestClient):
    response = client.post("/api/v5/events/retrogrades", json={"horizon_days": 2})
    assert response.status_code == 200

    body = response.json()
    assert body["status"] == "OK"
    assert body["horizon_days"] == 2
    assert body["planets"] == [
        "Mercury",
        "Venus",
        "Mars",
        "Jupiter",
        "Saturn",
        "Uranus",
        "Neptune",
        "Pluto",
    ]
    assert isinstance(body["events"], list)

    from_dt = datetime.fromisoformat(body["from_iso"])
    assert from_dt.tzinfo is not None
    assert from_dt.utcoffset() == timedelta(0)


def test_retrograde_events_rejects_from_iso_without_timezone(client: TestClient):
    payload = {
        "from_iso": "2026-03-01T00:00:00",
        "horizon_days": 30,
    }
    response = client.post("/api/v5/events/retrogrades", json=payload)
    assert response.status_code == 422


def test_retrograde_events_enforces_horizon_cap(client: TestClient):
    payload = {
        "horizon_days": 3651,
    }
    response = client.post("/api/v5/events/retrogrades", json=payload)
    assert response.status_code == 422


def test_retrograde_events_normalizes_and_deduplicates_planets(client: TestClient):
    payload = {
        "from_iso": "2026-03-01T00:00:00+00:00",
        "horizon_days": 10,
        "planets": ["mercury", "MERCURY", "venus"],
    }

    response = client.post("/api/v5/events/retrogrades", json=payload)
    assert response.status_code == 200
    body = response.json()

    assert body["planets"] == ["Mercury", "Venus"]
    assert all(item["planet"] in {"Mercury", "Venus"} for item in body["events"])


def test_retrograde_events_rejects_invalid_planets(client: TestClient):
    payload = {
        "horizon_days": 30,
        "planets": ["Mercury", "Sun"],
    }
    response = client.post("/api/v5/events/retrogrades", json=payload)
    assert response.status_code == 422


def test_retrograde_events_can_return_open_window_when_end_outside_horizon(client: TestClient):
    payload = {
        "from_iso": "2026-10-20T00:00:00+00:00",
        "horizon_days": 8,
        "planets": ["Mercury"],
    }
    response = client.post("/api/v5/events/retrogrades", json=payload)
    assert response.status_code == 200

    events = response.json()["events"]
    assert len(events) == 1
    event = events[0]
    assert event["event"] == "retrograde_period"
    assert event["planet"] == "Mercury"
    assert event["ends_at_utc"] is None
    assert event["end_speed"] is None


def test_retrograde_events_2026_match_online_reference_dates(client: TestClient):
    """
    Compares computed retrograde windows with an online UT-date reference table:
    https://www.astrosynthesis.com.au/wp-content/uploads/2025/12/2026-Retrogrades.pdf
    """
    assert REFERENCE_2026_SOURCE_URL.startswith("https://")

    for planet, expected_windows in REFERENCE_2026_WINDOWS_UT.items():
        actual_windows = _get_windows_starting_in_year(client, planet=planet, year=2026)
        assert actual_windows == expected_windows
