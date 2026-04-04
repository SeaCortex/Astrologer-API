from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Sequence

from kerykeion import AstrologicalSubjectFactory
from kerykeion.schemas import KerykeionException

CONJUNCTION_ALLOWED_PLANETS: tuple[str, ...] = (
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
)
CONJUNCTION_RAPID_PLANETS: tuple[str, ...] = ("Sun", "Moon", "Mercury", "Venus", "Mars")
CONJUNCTION_SLOW_PLANETS: tuple[str, ...] = ("Jupiter", "Saturn", "Uranus", "Neptune", "Pluto")
CONJUNCTION_DEFAULT_PLANETS: tuple[str, ...] = (
    "Sun",
    "Mercury",
    "Venus",
    "Mars",
    "Jupiter",
    "Saturn",
    "Uranus",
    "Neptune",
    "Pluto",
)
CONJUNCTION_ALLOWED_PAIR_TYPES: tuple[str, ...] = ("rapid_slow", "slow_slow", "rapid_rapid")
CONJUNCTION_DEFAULT_PAIR_TYPES: tuple[str, ...] = ("rapid_slow", "slow_slow")

CONJUNCTION_COARSE_SCAN_STEP_HOURS = 6
CONJUNCTION_REFINEMENT_STEP_MINUTES = 1
CONJUNCTION_MAX_HORIZON_DAYS = 3650
CONJUNCTION_MAX_REFINEMENT_ITERATIONS = 64
CONJUNCTION_WRAP_GUARD_DEGREES = 45.0
CONJUNCTION_DEDUPE_WINDOW_MINUTES = 30

_PLANET_LOOKUP: dict[str, str] = {planet.lower(): planet for planet in CONJUNCTION_ALLOWED_PLANETS}
_PAIR_TYPE_LOOKUP: dict[str, str] = {pair_type.lower(): pair_type for pair_type in CONJUNCTION_ALLOWED_PAIR_TYPES}
_PLANET_PRIORITY: dict[str, int] = {planet: index for index, planet in enumerate(CONJUNCTION_ALLOWED_PLANETS)}
_COARSE_SCAN_DELTA = timedelta(hours=CONJUNCTION_COARSE_SCAN_STEP_HOURS)
_REFINEMENT_DELTA = timedelta(minutes=CONJUNCTION_REFINEMENT_STEP_MINUTES)
_EVENT_DEDUPE_WINDOW = timedelta(minutes=CONJUNCTION_DEDUPE_WINDOW_MINUTES)


@dataclass(frozen=True)
class _PairDefinition:
    planet_1: str
    planet_2: str
    pair_type: str


def normalize_conjunction_planets(planets: Sequence[str]) -> list[str]:
    if not planets:
        raise ValueError("planets must contain at least two values.")

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
            allowed = ", ".join(CONJUNCTION_ALLOWED_PLANETS)
            raise ValueError(f"Invalid planet '{raw}'. Allowed values: {allowed}.")

        if canonical not in seen:
            seen.add(canonical)
            normalized.append(canonical)

    if len(normalized) < 2:
        raise ValueError("Provide at least two distinct planets to compute conjunction events.")

    return normalized


def normalize_conjunction_pair_types(pair_types: Sequence[str]) -> list[str]:
    if not pair_types:
        raise ValueError("pair_types must contain at least one value.")

    normalized: list[str] = []
    seen: set[str] = set()
    for raw in pair_types:
        if not isinstance(raw, str):
            raise ValueError("Each pair_type must be a string.")
        cleaned = raw.strip()
        if not cleaned:
            raise ValueError("pair_types values cannot be empty.")

        canonical = _PAIR_TYPE_LOOKUP.get(cleaned.lower())
        if not canonical:
            allowed = ", ".join(CONJUNCTION_ALLOWED_PAIR_TYPES)
            raise ValueError(f"Invalid pair_type '{raw}'. Allowed values: {allowed}.")

        if canonical not in seen:
            seen.add(canonical)
            normalized.append(canonical)

    return normalized


def _signed_separation_deg(p1_abs: float, p2_abs: float) -> float:
    separation = (p1_abs - p2_abs) % 360.0
    if separation > 180.0:
        separation -= 360.0
    return separation


def _pair_type_for(planet_1: str, planet_2: str) -> str:
    p1_is_rapid = planet_1 in CONJUNCTION_RAPID_PLANETS
    p2_is_rapid = planet_2 in CONJUNCTION_RAPID_PLANETS
    p1_is_slow = planet_1 in CONJUNCTION_SLOW_PLANETS
    p2_is_slow = planet_2 in CONJUNCTION_SLOW_PLANETS

    if p1_is_rapid and p2_is_rapid:
        return "rapid_rapid"
    if p1_is_slow and p2_is_slow:
        return "slow_slow"
    if (p1_is_rapid and p2_is_slow) or (p1_is_slow and p2_is_rapid):
        return "rapid_slow"

    raise KerykeionException(f"Unable to classify pair type for planets '{planet_1}' and '{planet_2}'.")


def _build_pair_definitions(planets: Sequence[str], selected_pair_types: set[str]) -> list[_PairDefinition]:
    # Stabilize pair ordering independent of request ordering.
    ordered_planets = sorted(planets, key=lambda item: _PLANET_PRIORITY[item])
    pairs: list[_PairDefinition] = []
    for first_index in range(len(ordered_planets)):
        for second_index in range(first_index + 1, len(ordered_planets)):
            planet_1 = ordered_planets[first_index]
            planet_2 = ordered_planets[second_index]
            pair_type = _pair_type_for(planet_1, planet_2)
            if pair_type in selected_pair_types:
                pairs.append(_PairDefinition(planet_1=planet_1, planet_2=planet_2, pair_type=pair_type))
    return pairs


def _get_planet_positions_and_speeds(at_utc: datetime, planets: Sequence[str]) -> dict[str, tuple[float, float]]:
    subject = AstrologicalSubjectFactory.from_iso_utc_time(
        name="Conjunction Scan",
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

    state: dict[str, tuple[float, float]] = {}
    for planet in planets:
        point = getattr(subject, planet.lower(), None)
        abs_pos = getattr(point, "abs_pos", None) if point is not None else None
        speed = getattr(point, "speed", None) if point is not None else None
        if abs_pos is None or speed is None:
            raise KerykeionException(f"Unable to compute position/speed for planet '{planet}'.")
        state[planet] = (float(abs_pos), float(speed))
    return state


def _get_signed_separation_for_pair(at_utc: datetime, pair: _PairDefinition) -> float:
    pair_state = _get_planet_positions_and_speeds(at_utc, [pair.planet_1, pair.planet_2])
    return _signed_separation_deg(pair_state[pair.planet_1][0], pair_state[pair.planet_2][0])


def _is_crossing_bracket(previous_sep: float, current_sep: float) -> bool:
    if previous_sep == 0.0 or current_sep == 0.0:
        return True
    if previous_sep * current_sep > 0.0:
        return False
    return abs(previous_sep) <= CONJUNCTION_WRAP_GUARD_DEGREES and abs(current_sep) <= CONJUNCTION_WRAP_GUARD_DEGREES


def _refine_conjunction_time_utc(
    *,
    pair: _PairDefinition,
    low_utc: datetime,
    high_utc: datetime,
    low_sep: float,
    high_sep: float,
) -> tuple[datetime, float]:
    if low_sep == 0.0:
        return low_utc, low_sep
    if high_sep == 0.0:
        return high_utc, high_sep

    if low_sep * high_sep > 0.0:
        raise KerykeionException(
            f"Cannot refine conjunction for {pair.planet_1}-{pair.planet_2}: bracket does not cross zero."
        )

    for _ in range(CONJUNCTION_MAX_REFINEMENT_ITERATIONS):
        if high_utc - low_utc <= _REFINEMENT_DELTA:
            break

        mid_utc = low_utc + (high_utc - low_utc) / 2
        mid_sep = _get_signed_separation_for_pair(mid_utc, pair)

        if mid_sep == 0.0:
            return mid_utc, mid_sep

        if low_sep * mid_sep > 0.0:
            low_utc = mid_utc
            low_sep = mid_sep
            continue

        high_utc = mid_utc
        high_sep = mid_sep

    return (low_utc, low_sep) if abs(low_sep) <= abs(high_sep) else (high_utc, high_sep)


def compute_conjunction_events(
    *,
    from_utc: datetime,
    horizon_days: int,
    planets: Sequence[str],
    pair_types: Sequence[str],
) -> list[dict]:
    if from_utc.tzinfo is None:
        raise KerykeionException("from_utc must include timezone information.")
    if horizon_days < 1:
        raise KerykeionException("horizon_days must be at least 1.")
    if horizon_days > CONJUNCTION_MAX_HORIZON_DAYS:
        raise KerykeionException(
            f"horizon_days exceeds maximum allowed ({CONJUNCTION_MAX_HORIZON_DAYS})."
        )

    normalized_planets = normalize_conjunction_planets(planets)
    normalized_pair_types = normalize_conjunction_pair_types(pair_types)
    selected_pair_types = set(normalized_pair_types)
    pair_definitions = _build_pair_definitions(normalized_planets, selected_pair_types)

    if not pair_definitions:
        return []

    start_utc = from_utc.astimezone(timezone.utc)
    end_utc = start_utc + timedelta(days=horizon_days)

    previous_utc = start_utc
    start_state = _get_planet_positions_and_speeds(previous_utc, normalized_planets)
    previous_separations: dict[tuple[str, str], float] = {}
    for pair in pair_definitions:
        previous_separations[(pair.planet_1, pair.planet_2)] = _signed_separation_deg(
            start_state[pair.planet_1][0], start_state[pair.planet_2][0]
        )

    last_event_by_pair: dict[tuple[str, str], datetime] = {}
    events: list[dict] = []

    while previous_utc < end_utc:
        current_utc = min(previous_utc + _COARSE_SCAN_DELTA, end_utc)
        current_state = _get_planet_positions_and_speeds(current_utc, normalized_planets)

        for pair in pair_definitions:
            pair_key = (pair.planet_1, pair.planet_2)
            previous_sep = previous_separations[pair_key]
            current_sep = _signed_separation_deg(
                current_state[pair.planet_1][0], current_state[pair.planet_2][0]
            )

            if _is_crossing_bracket(previous_sep, current_sep):
                event_utc, event_sep = _refine_conjunction_time_utc(
                    pair=pair,
                    low_utc=previous_utc,
                    high_utc=current_utc,
                    low_sep=previous_sep,
                    high_sep=current_sep,
                )

                if start_utc <= event_utc <= end_utc:
                    last_event_utc = last_event_by_pair.get(pair_key)
                    if last_event_utc is None or (event_utc - last_event_utc) > _EVENT_DEDUPE_WINDOW:
                        event_state = _get_planet_positions_and_speeds(event_utc, [pair.planet_1, pair.planet_2])
                        events.append(
                            {
                                "event": "planetary_conjunction",
                                "planet_1": pair.planet_1,
                                "planet_2": pair.planet_2,
                                "pair_type": pair.pair_type,
                                "at_utc": event_utc.isoformat(),
                                "orbit_deg": abs(event_sep),
                                "p1_speed": event_state[pair.planet_1][1],
                                "p2_speed": event_state[pair.planet_2][1],
                            }
                        )
                        last_event_by_pair[pair_key] = event_utc

            previous_separations[pair_key] = current_sep

        previous_utc = current_utc

    events.sort(key=lambda item: (item["at_utc"], item["planet_1"], item["planet_2"]))
    return events
