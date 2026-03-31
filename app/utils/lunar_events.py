from __future__ import annotations

import math
from datetime import datetime, timedelta, timezone
from typing import Final

from kerykeion import AstrologicalSubjectFactory
from kerykeion.schemas import KerykeionException

LUNAR_PHASE_EVENTS_MAX_HORIZON_DAYS = 730
LUNAR_EVENTS_COARSE_SCAN_STEP_HOURS = 6
LUNAR_EVENTS_REFINEMENT_STEP_MINUTES = 1
LUNAR_EVENTS_MAX_REFINEMENT_ITERATIONS = 64

LUNAR_EVENT_TARGETS: Final[tuple[tuple[str, float], ...]] = (
    ("new_moon", 0.0),
    ("first_quarter", 90.0),
    ("full_moon", 180.0),
    ("last_quarter", 270.0),
)

_COARSE_SCAN_DELTA = timedelta(hours=LUNAR_EVENTS_COARSE_SCAN_STEP_HOURS)
_REFINEMENT_DELTA = timedelta(minutes=LUNAR_EVENTS_REFINEMENT_STEP_MINUTES)


def _get_lunar_angle_utc(at_utc: datetime) -> float:
    subject = AstrologicalSubjectFactory.from_iso_utc_time(
        name="Lunar Events Scan",
        iso_utc_time=at_utc.isoformat(),
        city="Greenwich",
        nation="GB",
        tz_str="Etc/UTC",
        online=False,
        lng=-0.001545,
        lat=51.477928,
        active_points=["Sun", "Moon"],
        calculate_lunar_phase=True,
        suppress_geonames_warning=True,
    )

    phase = subject.lunar_phase
    if phase is None:
        raise KerykeionException("Unable to compute lunar phase for event detection.")
    return float(phase.degrees_between_s_m)


def _to_unwrapped_angle(raw_angle: float, anchor_low_unwrapped: float) -> float:
    base_cycle = math.floor(anchor_low_unwrapped / 360.0)
    candidate = raw_angle + (base_cycle * 360.0)
    if candidate < anchor_low_unwrapped:
        candidate += 360.0
    return candidate


def _refine_crossing_time_utc(
    low_utc: datetime,
    high_utc: datetime,
    low_unwrapped: float,
    high_unwrapped: float,
    target_unwrapped: float,
) -> tuple[datetime, float]:
    if not (low_unwrapped <= target_unwrapped <= high_unwrapped):
        raise KerykeionException("Lunar event bracket does not include the target crossing.")

    anchor_low_unwrapped = low_unwrapped
    for _ in range(LUNAR_EVENTS_MAX_REFINEMENT_ITERATIONS):
        if high_utc - low_utc <= _REFINEMENT_DELTA:
            break

        mid_utc = low_utc + (high_utc - low_utc) / 2
        mid_raw = _get_lunar_angle_utc(mid_utc)
        mid_unwrapped = _to_unwrapped_angle(mid_raw, anchor_low_unwrapped)

        if mid_unwrapped < target_unwrapped:
            low_utc = mid_utc
            low_unwrapped = mid_unwrapped
            continue

        high_utc = mid_utc
        high_unwrapped = mid_unwrapped

    event_raw = _get_lunar_angle_utc(high_utc)
    event_unwrapped = _to_unwrapped_angle(event_raw, anchor_low_unwrapped)
    return high_utc, event_unwrapped % 360.0


def compute_lunar_phase_events(from_utc: datetime, horizon_days: int) -> list[dict]:
    if from_utc.tzinfo is None:
        raise KerykeionException("from_utc must include timezone information.")
    if horizon_days < 1:
        raise KerykeionException("horizon_days must be at least 1.")
    if horizon_days > LUNAR_PHASE_EVENTS_MAX_HORIZON_DAYS:
        raise KerykeionException(
            f"horizon_days exceeds maximum allowed ({LUNAR_PHASE_EVENTS_MAX_HORIZON_DAYS})."
        )

    start_utc = from_utc.astimezone(timezone.utc)
    end_utc = start_utc + timedelta(days=horizon_days)

    events: list[dict] = []

    previous_utc = start_utc
    previous_raw = _get_lunar_angle_utc(previous_utc)
    wrap_count = 0
    previous_unwrapped = previous_raw

    while previous_utc < end_utc:
        current_utc = min(previous_utc + _COARSE_SCAN_DELTA, end_utc)
        current_raw = _get_lunar_angle_utc(current_utc)
        if current_raw < previous_raw:
            wrap_count += 1

        current_unwrapped = current_raw + (wrap_count * 360.0)

        for event_name, target_angle in LUNAR_EVENT_TARGETS:
            cycle_index = math.floor((previous_unwrapped - target_angle) / 360.0) + 1
            crossing_unwrapped = target_angle + (cycle_index * 360.0)

            while crossing_unwrapped <= current_unwrapped:
                event_utc, event_angle = _refine_crossing_time_utc(
                    low_utc=previous_utc,
                    high_utc=current_utc,
                    low_unwrapped=previous_unwrapped,
                    high_unwrapped=current_unwrapped,
                    target_unwrapped=crossing_unwrapped,
                )
                if start_utc <= event_utc <= end_utc:
                    events.append(
                        {
                            "event": event_name,
                            "at_utc": event_utc.isoformat(),
                            "target_angle_deg": target_angle,
                            "angle_deg": event_angle,
                        }
                    )
                crossing_unwrapped += 360.0

        previous_utc = current_utc
        previous_raw = current_raw
        previous_unwrapped = current_unwrapped

    events.sort(key=lambda event: event["at_utc"])
    return events
