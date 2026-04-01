from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Sequence

from kerykeion import AstrologicalSubjectFactory
from kerykeion.schemas import KerykeionException

from .conjunctions import (
    CONJUNCTION_ALLOWED_PLANETS,
    CONJUNCTION_DEFAULT_PAIR_TYPES,
    CONJUNCTION_DEFAULT_PLANETS,
    CONJUNCTION_RAPID_PLANETS,
    CONJUNCTION_SLOW_PLANETS,
    normalize_conjunction_pair_types,
    normalize_conjunction_planets,
)

ASPECT_EVENTS_ALLOWED_ASPECT_TYPES: tuple[str, ...] = ("square", "opposition")
ASPECT_EVENTS_DEFAULT_ASPECT_TYPES: tuple[str, ...] = ("square", "opposition")

ASPECT_EVENTS_COARSE_SCAN_STEP_HOURS = 6
ASPECT_EVENTS_REFINEMENT_STEP_MINUTES = 1
ASPECT_EVENTS_MAX_HORIZON_DAYS = 3650
ASPECT_EVENTS_MAX_REFINEMENT_ITERATIONS = 64
ASPECT_EVENTS_WRAP_GUARD_DEGREES = 45.0
ASPECT_EVENTS_DEDUPE_WINDOW_MINUTES = 30

_ASPECT_TYPE_LOOKUP: dict[str, str] = {
    aspect_type.lower(): aspect_type for aspect_type in ASPECT_EVENTS_ALLOWED_ASPECT_TYPES
}
_PLANET_PRIORITY: dict[str, int] = {
    planet: index for index, planet in enumerate(CONJUNCTION_ALLOWED_PLANETS)
}
_COARSE_SCAN_DELTA = timedelta(hours=ASPECT_EVENTS_COARSE_SCAN_STEP_HOURS)
_REFINEMENT_DELTA = timedelta(minutes=ASPECT_EVENTS_REFINEMENT_STEP_MINUTES)
_EVENT_DEDUPE_WINDOW = timedelta(minutes=ASPECT_EVENTS_DEDUPE_WINDOW_MINUTES)


@dataclass(frozen=True)
class _PairDefinition:
    planet_1: str
    planet_2: str
    pair_type: str


@dataclass(frozen=True)
class _PairAspectTargetDefinition:
    pair: _PairDefinition
    aspect: str
    target_angle_deg: float


def normalize_aspect_event_aspect_types(aspect_types: Sequence[str]) -> list[str]:
    if not aspect_types:
        raise ValueError("aspect_types must contain at least one value.")

    normalized: list[str] = []
    seen: set[str] = set()
    for raw in aspect_types:
        if not isinstance(raw, str):
            raise ValueError("Each aspect_type must be a string.")
        cleaned = raw.strip()
        if not cleaned:
            raise ValueError("aspect_types values cannot be empty.")

        canonical = _ASPECT_TYPE_LOOKUP.get(cleaned.lower())
        if not canonical:
            allowed = ", ".join(ASPECT_EVENTS_ALLOWED_ASPECT_TYPES)
            raise ValueError(f"Invalid aspect_type '{raw}'. Allowed values: {allowed}.")

        if canonical not in seen:
            seen.add(canonical)
            normalized.append(canonical)

    return normalized


def _directed_separation_deg(p1_abs: float, p2_abs: float) -> float:
    return (p1_abs - p2_abs) % 360.0


def _signed_offset_from_target(separation_deg: float, target_angle_deg: float) -> float:
    return ((separation_deg - target_angle_deg + 180.0) % 360.0) - 180.0


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


def _targets_for_aspect(aspect: str) -> tuple[float, ...]:
    if aspect == "square":
        return (90.0, 270.0)
    if aspect == "opposition":
        return (180.0,)
    raise KerykeionException(f"Unsupported aspect type '{aspect}'.")


def _build_pair_aspect_targets(
    pair_definitions: Sequence[_PairDefinition], aspect_types: Sequence[str]
) -> list[_PairAspectTargetDefinition]:
    targets: list[_PairAspectTargetDefinition] = []
    for pair in pair_definitions:
        for aspect in aspect_types:
            for target_angle in _targets_for_aspect(aspect):
                targets.append(
                    _PairAspectTargetDefinition(
                        pair=pair,
                        aspect=aspect,
                        target_angle_deg=target_angle,
                    )
                )
    return targets


def _get_planet_positions_and_speeds(at_utc: datetime, planets: Sequence[str]) -> dict[str, tuple[float, float]]:
    subject = AstrologicalSubjectFactory.from_iso_utc_time(
        name="Aspect Events Scan",
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


def _signed_offset_for_pair_target(at_utc: datetime, pair_target: _PairAspectTargetDefinition) -> float:
    pair_state = _get_planet_positions_and_speeds(
        at_utc, [pair_target.pair.planet_1, pair_target.pair.planet_2]
    )
    separation = _directed_separation_deg(
        pair_state[pair_target.pair.planet_1][0],
        pair_state[pair_target.pair.planet_2][0],
    )
    return _signed_offset_from_target(separation, pair_target.target_angle_deg)


def _is_crossing_bracket(previous_offset: float, current_offset: float) -> bool:
    if previous_offset == 0.0 or current_offset == 0.0:
        return True
    if previous_offset * current_offset > 0.0:
        return False
    return (
        abs(previous_offset) <= ASPECT_EVENTS_WRAP_GUARD_DEGREES
        and abs(current_offset) <= ASPECT_EVENTS_WRAP_GUARD_DEGREES
    )


def _refine_pair_target_time_utc(
    *,
    pair_target: _PairAspectTargetDefinition,
    low_utc: datetime,
    high_utc: datetime,
    low_offset: float,
    high_offset: float,
) -> tuple[datetime, float]:
    if low_offset == 0.0:
        return low_utc, low_offset
    if high_offset == 0.0:
        return high_utc, high_offset

    if low_offset * high_offset > 0.0:
        raise KerykeionException(
            "Cannot refine aspect event for "
            f"{pair_target.pair.planet_1}-{pair_target.pair.planet_2} {pair_target.aspect}: "
            "bracket does not cross zero."
        )

    for _ in range(ASPECT_EVENTS_MAX_REFINEMENT_ITERATIONS):
        if high_utc - low_utc <= _REFINEMENT_DELTA:
            break

        mid_utc = low_utc + (high_utc - low_utc) / 2
        mid_offset = _signed_offset_for_pair_target(mid_utc, pair_target)

        if mid_offset == 0.0:
            return mid_utc, mid_offset

        if low_offset * mid_offset > 0.0:
            low_utc = mid_utc
            low_offset = mid_offset
            continue

        high_utc = mid_utc
        high_offset = mid_offset

    return (low_utc, low_offset) if abs(low_offset) <= abs(high_offset) else (high_utc, high_offset)


def compute_aspect_events(
    *,
    from_utc: datetime,
    horizon_days: int,
    planets: Sequence[str],
    pair_types: Sequence[str],
    aspect_types: Sequence[str],
) -> list[dict]:
    if from_utc.tzinfo is None:
        raise KerykeionException("from_utc must include timezone information.")
    if horizon_days < 1:
        raise KerykeionException("horizon_days must be at least 1.")
    if horizon_days > ASPECT_EVENTS_MAX_HORIZON_DAYS:
        raise KerykeionException(
            f"horizon_days exceeds maximum allowed ({ASPECT_EVENTS_MAX_HORIZON_DAYS})."
        )

    normalized_planets = normalize_conjunction_planets(planets)
    normalized_pair_types = normalize_conjunction_pair_types(pair_types)
    normalized_aspect_types = normalize_aspect_event_aspect_types(aspect_types)

    selected_pair_types = set(normalized_pair_types)
    pair_definitions = _build_pair_definitions(normalized_planets, selected_pair_types)
    if not pair_definitions:
        return []

    pair_targets = _build_pair_aspect_targets(pair_definitions, normalized_aspect_types)
    if not pair_targets:
        return []

    start_utc = from_utc.astimezone(timezone.utc)
    end_utc = start_utc + timedelta(days=horizon_days)

    previous_utc = start_utc
    start_state = _get_planet_positions_and_speeds(previous_utc, normalized_planets)
    previous_offsets: dict[tuple[str, str, str, float], float] = {}
    for pair_target in pair_targets:
        pair = pair_target.pair
        pair_key = (pair.planet_1, pair.planet_2, pair_target.aspect, pair_target.target_angle_deg)
        separation = _directed_separation_deg(
            start_state[pair.planet_1][0],
            start_state[pair.planet_2][0],
        )
        previous_offsets[pair_key] = _signed_offset_from_target(separation, pair_target.target_angle_deg)

    last_event_by_pair_target: dict[tuple[str, str, str, float], datetime] = {}
    events: list[dict] = []

    while previous_utc < end_utc:
        current_utc = min(previous_utc + _COARSE_SCAN_DELTA, end_utc)
        current_state = _get_planet_positions_and_speeds(current_utc, normalized_planets)

        for pair_target in pair_targets:
            pair = pair_target.pair
            pair_key = (pair.planet_1, pair.planet_2, pair_target.aspect, pair_target.target_angle_deg)
            previous_offset = previous_offsets[pair_key]
            current_separation = _directed_separation_deg(
                current_state[pair.planet_1][0],
                current_state[pair.planet_2][0],
            )
            current_offset = _signed_offset_from_target(current_separation, pair_target.target_angle_deg)

            if _is_crossing_bracket(previous_offset, current_offset):
                event_utc, event_offset = _refine_pair_target_time_utc(
                    pair_target=pair_target,
                    low_utc=previous_utc,
                    high_utc=current_utc,
                    low_offset=previous_offset,
                    high_offset=current_offset,
                )

                if start_utc <= event_utc <= end_utc:
                    last_event_utc = last_event_by_pair_target.get(pair_key)
                    if last_event_utc is None or (event_utc - last_event_utc) > _EVENT_DEDUPE_WINDOW:
                        event_state = _get_planet_positions_and_speeds(event_utc, [pair.planet_1, pair.planet_2])
                        events.append(
                            {
                                "event": "planetary_aspect",
                                "aspect": pair_target.aspect,
                                "planet_1": pair.planet_1,
                                "planet_2": pair.planet_2,
                                "pair_type": pair.pair_type,
                                "target_angle_deg": pair_target.target_angle_deg,
                                "at_utc": event_utc.isoformat(),
                                "orbit_deg": abs(event_offset),
                                "p1_speed": event_state[pair.planet_1][1],
                                "p2_speed": event_state[pair.planet_2][1],
                            }
                        )
                        last_event_by_pair_target[pair_key] = event_utc

            previous_offsets[pair_key] = current_offset

        previous_utc = current_utc

    events.sort(
        key=lambda item: (
            item["at_utc"],
            item["planet_1"],
            item["planet_2"],
            item["aspect"],
            item["target_angle_deg"],
        )
    )
    return events


__all__ = [
    "ASPECT_EVENTS_ALLOWED_ASPECT_TYPES",
    "ASPECT_EVENTS_DEFAULT_ASPECT_TYPES",
    "ASPECT_EVENTS_MAX_HORIZON_DAYS",
    "compute_aspect_events",
    "normalize_aspect_event_aspect_types",
    # Re-exported for request model defaults parity with conjunction endpoint.
    "CONJUNCTION_DEFAULT_PLANETS",
    "CONJUNCTION_DEFAULT_PAIR_TYPES",
]
