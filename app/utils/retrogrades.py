from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Optional, Sequence

from kerykeion import AstrologicalSubjectFactory
from kerykeion.schemas import KerykeionException

RETROGRADE_ALLOWED_PLANETS: tuple[str, ...] = (
    "Mercury",
    "Venus",
    "Mars",
    "Jupiter",
    "Saturn",
    "Uranus",
    "Neptune",
    "Pluto",
)
RETROGRADE_DEFAULT_PLANETS: tuple[str, ...] = RETROGRADE_ALLOWED_PLANETS
RETROGRADE_COARSE_SCAN_STEP_HOURS = 6
RETROGRADE_REFINEMENT_STEP_MINUTES = 1
RETROGRADE_MAX_HORIZON_DAYS = 3650
RETROGRADE_MAX_REFINEMENT_ITERATIONS = 64

_PLANET_LOOKUP: dict[str, str] = {planet.lower(): planet for planet in RETROGRADE_ALLOWED_PLANETS}
_COARSE_SCAN_DELTA = timedelta(hours=RETROGRADE_COARSE_SCAN_STEP_HOURS)
_REFINEMENT_DELTA = timedelta(minutes=RETROGRADE_REFINEMENT_STEP_MINUTES)


@dataclass
class _PlanetState:
    previous_speed: float
    previous_retrograde: bool
    start_time_utc: Optional[datetime]
    start_speed: Optional[float]


def normalize_retrograde_planets(planets: Sequence[str]) -> list[str]:
    if not planets:
        raise ValueError("planets must contain at least one value.")

    normalized: list[str] = []
    seen: set[str] = set()

    for raw in planets:
        if not isinstance(raw, str):
            raise ValueError("Each planet must be a string.")
        cleaned = raw.strip()
        if not cleaned:
            raise ValueError("Planet names cannot be empty.")

        canonical = _PLANET_LOOKUP.get(cleaned.lower())
        if not canonical:
            allowed = ", ".join(RETROGRADE_ALLOWED_PLANETS)
            raise ValueError(f"Invalid planet '{raw}'. Allowed values: {allowed}.")

        if canonical not in seen:
            seen.add(canonical)
            normalized.append(canonical)

    return normalized


def parse_iso_utc(value: str) -> datetime:
    try:
        dt = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise KerykeionException(f"Invalid ISO datetime: {value}") from exc
    if dt.tzinfo is None:
        raise KerykeionException(f"Timezone offset is required: {value}")
    return dt.astimezone(timezone.utc)


def _get_planet_speeds(at_utc: datetime, planets: Sequence[str]) -> dict[str, float]:
    subject = AstrologicalSubjectFactory.from_iso_utc_time(
        name="Retrograde Scan",
        iso_utc_time=at_utc.isoformat(),
        city="Greenwich",
        nation="GB",
        tz_str="Etc/UTC",
        online=False,
        lng=-0.001545,
        lat=51.477928,
        active_points=list(planets),
        calculate_lunar_phase=False,
        suppress_geonames_warning=True,
    )

    speeds: dict[str, float] = {}
    for planet in planets:
        point = getattr(subject, planet.lower(), None)
        speed = getattr(point, "speed", None) if point is not None else None
        if speed is None:
            raise KerykeionException(f"Unable to compute speed for planet '{planet}'.")
        speeds[planet] = float(speed)
    return speeds


def _refine_flip_time_utc(
    planet: str,
    low_utc: datetime,
    high_utc: datetime,
    low_speed: float,
    high_speed: float,
) -> tuple[datetime, float]:
    low_retrograde = low_speed < 0
    high_retrograde = high_speed < 0
    if low_retrograde == high_retrograde:
        raise KerykeionException(
            f"Cannot refine retrograde flip for {planet}: bracket does not cross motion state."
        )

    for _ in range(RETROGRADE_MAX_REFINEMENT_ITERATIONS):
        if high_utc - low_utc <= _REFINEMENT_DELTA:
            break
        mid_utc = low_utc + (high_utc - low_utc) / 2
        mid_speed = _get_planet_speeds(mid_utc, [planet])[planet]
        mid_retrograde = mid_speed < 0

        if mid_retrograde == low_retrograde:
            low_utc = mid_utc
            low_speed = mid_speed
            continue

        high_utc = mid_utc
        high_speed = mid_speed

    return high_utc, high_speed


def _build_event_result(
    *,
    planet: str,
    start_time_utc: datetime,
    end_time_utc: Optional[datetime],
    start_speed: Optional[float],
    end_speed: Optional[float],
) -> dict:
    return {
        "event": "retrograde_period",
        "planet": planet,
        "at_utc": start_time_utc.isoformat(),
        "ends_at_utc": end_time_utc.isoformat() if end_time_utc else None,
        "start_speed": start_speed,
        "end_speed": end_speed,
    }


def compute_retrograde_events(
    from_utc: datetime,
    horizon_days: int,
    planets: Sequence[str],
) -> list[dict]:
    if from_utc.tzinfo is None:
        raise KerykeionException("from_utc must include timezone information.")
    if horizon_days < 1:
        raise KerykeionException("horizon_days must be at least 1.")
    if horizon_days > RETROGRADE_MAX_HORIZON_DAYS:
        raise KerykeionException(
            f"horizon_days exceeds maximum allowed ({RETROGRADE_MAX_HORIZON_DAYS})."
        )

    normalized_planets = normalize_retrograde_planets(planets)
    start_utc = from_utc.astimezone(timezone.utc)
    end_utc = start_utc + timedelta(days=horizon_days)

    initial_speeds = _get_planet_speeds(start_utc, normalized_planets)
    states: dict[str, _PlanetState] = {}
    for planet in normalized_planets:
        initial_speed = initial_speeds[planet]
        initial_retrograde = initial_speed < 0
        states[planet] = _PlanetState(
            previous_speed=initial_speed,
            previous_retrograde=initial_retrograde,
            start_time_utc=None,
            start_speed=None,
        )

    events: list[dict] = []
    previous_utc = start_utc
    while previous_utc < end_utc:
        current_utc = min(previous_utc + _COARSE_SCAN_DELTA, end_utc)
        current_speeds = _get_planet_speeds(current_utc, normalized_planets)

        for planet in normalized_planets:
            state = states[planet]
            previous_speed = state.previous_speed
            current_speed = current_speeds[planet]
            previous_retrograde = state.previous_retrograde
            current_retrograde = current_speed < 0

            if current_retrograde != previous_retrograde:
                flip_time_utc, flip_speed = _refine_flip_time_utc(
                    planet=planet,
                    low_utc=previous_utc,
                    high_utc=current_utc,
                    low_speed=previous_speed,
                    high_speed=current_speed,
                )

                if (not previous_retrograde) and current_retrograde:
                    state.start_time_utc = flip_time_utc
                    state.start_speed = flip_speed
                elif previous_retrograde and (not current_retrograde):
                    if state.start_time_utc is not None:
                        events.append(
                            _build_event_result(
                                planet=planet,
                                start_time_utc=state.start_time_utc,
                                end_time_utc=flip_time_utc,
                                start_speed=state.start_speed,
                                end_speed=flip_speed,
                            )
                        )
                        state.start_time_utc = None
                        state.start_speed = None

            state.previous_speed = current_speed
            state.previous_retrograde = current_retrograde

        previous_utc = current_utc

    for planet in normalized_planets:
        state = states[planet]
        if state.start_time_utc is None:
            continue
        events.append(
            _build_event_result(
                planet=planet,
                start_time_utc=state.start_time_utc,
                end_time_utc=None,
                start_speed=state.start_speed,
                end_speed=None,
            )
        )

    events.sort(key=lambda item: (item["at_utc"], item["planet"]))
    return events
