from __future__ import annotations

from datetime import datetime, timedelta, timezone

from fastapi.testclient import TestClient

TARGET_ANGLE_BY_EVENT = {
    "new_moon": 0.0,
    "first_quarter": 90.0,
    "full_moon": 180.0,
    "last_quarter": 270.0,
}

REFERENCE_2026_SOURCE_URL = "https://www.astropixels.com/almanac/almanac21/almanac2026gmt.html"
# UTC phase times extracted from the source above (accessed 2026-03-31), section:
# "2026 Phases of the Moon / Greenwich Mean Time".
REFERENCE_2026_PHASES_UTC: list[tuple[str, str]] = [
    ("full_moon", "2026-01-03T10:03:00+00:00"),
    ("last_quarter", "2026-01-10T15:48:00+00:00"),
    ("new_moon", "2026-01-18T19:52:00+00:00"),
    ("first_quarter", "2026-01-26T04:47:00+00:00"),
    ("full_moon", "2026-02-01T22:09:00+00:00"),
    ("last_quarter", "2026-02-09T12:43:00+00:00"),
    ("new_moon", "2026-02-17T12:01:00+00:00"),
    ("first_quarter", "2026-02-24T12:28:00+00:00"),
    ("full_moon", "2026-03-03T11:38:00+00:00"),
    ("last_quarter", "2026-03-11T09:39:00+00:00"),
    ("new_moon", "2026-03-19T01:23:00+00:00"),
    ("first_quarter", "2026-03-25T19:18:00+00:00"),
    ("full_moon", "2026-04-02T02:12:00+00:00"),
    ("last_quarter", "2026-04-10T04:52:00+00:00"),
    ("new_moon", "2026-04-17T11:52:00+00:00"),
    ("first_quarter", "2026-04-24T02:32:00+00:00"),
    ("full_moon", "2026-05-01T17:23:00+00:00"),
    ("last_quarter", "2026-05-09T21:10:00+00:00"),
    ("new_moon", "2026-05-16T20:01:00+00:00"),
    ("first_quarter", "2026-05-23T11:11:00+00:00"),
    ("full_moon", "2026-05-31T08:45:00+00:00"),
    ("last_quarter", "2026-06-08T10:00:00+00:00"),
    ("new_moon", "2026-06-15T02:54:00+00:00"),
    ("first_quarter", "2026-06-21T21:55:00+00:00"),
    ("full_moon", "2026-06-29T23:57:00+00:00"),
    ("last_quarter", "2026-07-07T19:29:00+00:00"),
    ("new_moon", "2026-07-14T09:43:00+00:00"),
    ("first_quarter", "2026-07-21T11:06:00+00:00"),
    ("full_moon", "2026-07-29T14:36:00+00:00"),
    ("last_quarter", "2026-08-06T02:21:00+00:00"),
    ("new_moon", "2026-08-12T17:37:00+00:00"),
    ("first_quarter", "2026-08-20T02:46:00+00:00"),
    ("full_moon", "2026-08-28T04:18:00+00:00"),
    ("last_quarter", "2026-09-04T07:51:00+00:00"),
    ("new_moon", "2026-09-11T03:27:00+00:00"),
    ("first_quarter", "2026-09-18T20:44:00+00:00"),
    ("full_moon", "2026-09-26T16:49:00+00:00"),
    ("last_quarter", "2026-10-03T13:25:00+00:00"),
    ("new_moon", "2026-10-10T15:50:00+00:00"),
    ("first_quarter", "2026-10-18T16:13:00+00:00"),
    ("full_moon", "2026-10-26T04:12:00+00:00"),
    ("last_quarter", "2026-11-01T20:28:00+00:00"),
    ("new_moon", "2026-11-09T07:02:00+00:00"),
    ("first_quarter", "2026-11-17T11:48:00+00:00"),
    ("full_moon", "2026-11-24T14:53:00+00:00"),
    ("last_quarter", "2026-12-01T06:09:00+00:00"),
    ("new_moon", "2026-12-09T00:52:00+00:00"),
    ("first_quarter", "2026-12-17T05:43:00+00:00"),
    ("full_moon", "2026-12-24T01:28:00+00:00"),
    ("last_quarter", "2026-12-30T18:59:00+00:00"),
]


def _angular_distance(a: float, b: float) -> float:
    return abs(((a - b + 180.0) % 360.0) - 180.0)


def test_lunar_phase_events_returns_sorted_events_with_refined_angles(client: TestClient):
    payload = {
        "from_iso": "2026-03-01T00:00:00+00:00",
        "horizon_days": 40,
    }

    response = client.post("/api/v5/events/lunar-phases", json=payload)
    assert response.status_code == 200

    body = response.json()
    assert body["status"] == "OK"
    assert body["from_iso"] == "2026-03-01T00:00:00+00:00"
    assert body["horizon_days"] == 40

    events = body["events"]
    assert events, "Expected at least one lunar event in a 40-day window."

    from_dt = datetime.fromisoformat(body["from_iso"]).astimezone(timezone.utc)
    horizon_dt = from_dt + timedelta(days=body["horizon_days"])

    previous_dt: datetime | None = None
    for item in events:
        event_name = item["event"]
        assert event_name in TARGET_ANGLE_BY_EVENT

        at_dt = datetime.fromisoformat(item["at_utc"]).astimezone(timezone.utc)
        assert from_dt <= at_dt <= horizon_dt
        if previous_dt is not None:
            assert at_dt >= previous_dt
        previous_dt = at_dt

        target_angle = TARGET_ANGLE_BY_EVENT[event_name]
        assert item["target_angle_deg"] == target_angle
        assert _angular_distance(item["angle_deg"], target_angle) <= 0.05

    # From 2026-03-01, the first quarter-event crossing in this engine is Full Moon.
    assert events[0]["event"] == "full_moon"


def test_lunar_phase_events_defaults_from_iso_to_current_utc(client: TestClient):
    response = client.post("/api/v5/events/lunar-phases", json={"horizon_days": 5})
    assert response.status_code == 200

    body = response.json()
    assert body["status"] == "OK"
    assert body["horizon_days"] == 5
    assert isinstance(body["events"], list)

    from_dt = datetime.fromisoformat(body["from_iso"])
    assert from_dt.tzinfo is not None
    assert from_dt.utcoffset() == timedelta(0)


def test_lunar_phase_events_rejects_from_iso_without_timezone(client: TestClient):
    payload = {
        "from_iso": "2026-03-01T00:00:00",
        "horizon_days": 30,
    }
    response = client.post("/api/v5/events/lunar-phases", json=payload)
    assert response.status_code == 422


def test_lunar_phase_events_enforces_horizon_cap(client: TestClient):
    payload = {
        "horizon_days": 731,
    }
    response = client.post("/api/v5/events/lunar-phases", json=payload)
    assert response.status_code == 422


def test_lunar_phase_events_2026_match_reference_utc_times(client: TestClient):
    """
    Compares computed 2026 lunar phase instants with the online UTC reference table:
    https://www.astropixels.com/almanac/almanac21/almanac2026gmt.html
    """
    assert REFERENCE_2026_SOURCE_URL.startswith("https://")

    response = client.post(
        "/api/v5/events/lunar-phases",
        json={
            "from_iso": "2026-01-01T00:00:00+00:00",
            "horizon_days": 365,
        },
    )
    assert response.status_code == 200

    events = response.json()["events"]
    assert len(events) == len(REFERENCE_2026_PHASES_UTC)

    for computed, (expected_event, expected_iso) in zip(events, REFERENCE_2026_PHASES_UTC, strict=True):
        assert computed["event"] == expected_event

        computed_dt = datetime.fromisoformat(computed["at_utc"]).astimezone(timezone.utc)
        expected_dt = datetime.fromisoformat(expected_iso).astimezone(timezone.utc)
        # Source table provides minute precision. Keep a conservative tolerance.
        assert abs((computed_dt - expected_dt).total_seconds()) <= 300
