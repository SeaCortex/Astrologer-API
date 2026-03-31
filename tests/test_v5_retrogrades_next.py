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
    from_dt = datetime(year, 1, 1, tzinfo=timezone.utc)
    windows: list[tuple[str, str]] = []

    # Hard upper bound to avoid accidental infinite loops on endpoint regressions.
    for _ in range(8):
        response = client.post(
            "/api/v5/retrogrades/next",
            json={
                "from_iso": from_dt.isoformat(),
                "horizon_days": 500,
                "planets": [planet],
                "include_ongoing": False,
            },
        )
        assert response.status_code == 200

        retrograde = response.json()["retrogrades"][0]
        start_iso = retrograde["next_start_utc"]
        end_iso = retrograde["next_end_utc"]
        if start_iso is None:
            break

        start_dt = datetime.fromisoformat(start_iso).astimezone(timezone.utc)
        if start_dt.year != year:
            break

        assert end_iso is not None
        end_dt = datetime.fromisoformat(end_iso).astimezone(timezone.utc)
        windows.append((start_dt.date().isoformat(), end_dt.date().isoformat()))
        from_dt = end_dt + timedelta(minutes=1)

    return windows


def test_retrogrades_next_include_ongoing_true_returns_current_window(client: TestClient):
    payload = {
        "from_iso": "2024-08-10T00:00:00+00:00",
        "horizon_days": 60,
        "planets": ["Mercury"],
        "include_ongoing": True,
    }

    response = client.post("/api/v5/retrogrades/next", json=payload)
    assert response.status_code == 200

    body = response.json()
    assert body["status"] == "OK"
    assert body["from_iso"].startswith("2024-08-10T00:00:00+00:00")
    assert body["horizon_days"] == 60
    assert body["include_ongoing"] is True

    retrograde = body["retrogrades"][0]
    assert retrograde["planet"] == "Mercury"
    assert retrograde["is_ongoing"] is True
    assert retrograde["started_before_from"] is True
    assert retrograde["start_speed"] is not None and retrograde["start_speed"] < 0
    assert retrograde["next_end_utc"] is not None
    assert retrograde["end_speed"] is not None and retrograde["end_speed"] > 0


def test_retrogrades_next_include_ongoing_false_returns_strictly_future_window(client: TestClient):
    from_iso = "2024-08-10T00:00:00+00:00"
    payload = {
        "from_iso": from_iso,
        "horizon_days": 150,
        "planets": ["Mercury"],
        "include_ongoing": False,
    }

    response = client.post("/api/v5/retrogrades/next", json=payload)
    assert response.status_code == 200

    body = response.json()
    retrograde = body["retrogrades"][0]

    assert retrograde["planet"] == "Mercury"
    assert retrograde["is_ongoing"] is False
    assert retrograde["started_before_from"] is False
    assert retrograde["next_start_utc"] is not None
    assert retrograde["next_end_utc"] is not None
    assert retrograde["start_speed"] is not None and retrograde["start_speed"] < 0
    assert retrograde["end_speed"] is not None and retrograde["end_speed"] > 0

    start_dt = datetime.fromisoformat(retrograde["next_start_utc"]).astimezone(timezone.utc)
    from_dt = datetime.fromisoformat(from_iso).astimezone(timezone.utc)
    assert start_dt > from_dt


def test_retrogrades_next_normalizes_and_deduplicates_planets(client: TestClient):
    payload = {
        "from_iso": "2024-08-10T00:00:00+00:00",
        "horizon_days": 30,
        "planets": ["mercury", "MERCURY", "venus"],
    }

    response = client.post("/api/v5/retrogrades/next", json=payload)
    assert response.status_code == 200
    body = response.json()

    assert [item["planet"] for item in body["retrogrades"]] == ["Mercury", "Venus"]


def test_retrogrades_next_rejects_invalid_planets(client: TestClient):
    payload = {
        "horizon_days": 30,
        "planets": ["Mercury", "Sun"],
    }
    response = client.post("/api/v5/retrogrades/next", json=payload)
    assert response.status_code == 422


def test_retrogrades_next_enforces_horizon_cap(client: TestClient):
    payload = {
        "horizon_days": 731,
        "planets": ["Mercury"],
    }
    response = client.post("/api/v5/retrogrades/next", json=payload)
    assert response.status_code == 422


def test_retrogrades_2026_match_online_reference_dates(client: TestClient):
    """
    Compares computed retrograde windows with an online UT-date reference table:
    https://www.astrosynthesis.com.au/wp-content/uploads/2025/12/2026-Retrogrades.pdf
    """
    assert REFERENCE_2026_SOURCE_URL.startswith("https://")

    for planet, expected_windows in REFERENCE_2026_WINDOWS_UT.items():
        actual_windows = _get_windows_starting_in_year(client, planet=planet, year=2026)
        assert actual_windows == expected_windows
