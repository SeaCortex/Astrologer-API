from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Sequence

from kerykeion import AstrologicalSubjectFactory
from kerykeion.schemas import KerykeionException

INGRESS_ALLOWED_PLANETS: tuple[str, ...] = (
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
    "Mean_Lilith",
    "True_Lilith",
)
INGRESS_DEFAULT_PLANETS: tuple[str, ...] = (
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
INGRESS_COARSE_SCAN_STEP_HOURS = 6
INGRESS_REFINEMENT_STEP_MINUTES = 1
INGRESS_MAX_HORIZON_DAYS = 730
INGRESS_MAX_REFINEMENT_ITERATIONS = 64

_PLANET_LOOKUP: dict[str, str] = {
    planet.lower(): planet for planet in INGRESS_ALLOWED_PLANETS
}
_COARSE_SCAN_DELTA = timedelta(hours=INGRESS_COARSE_SCAN_STEP_HOURS)
_REFINEMENT_DELTA = timedelta(minutes=INGRESS_REFINEMENT_STEP_MINUTES)


def normalize_ingress_planets(planets: Sequence[str]) -> list[str]:
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
            allowed = ", ".join(INGRESS_ALLOWED_PLANETS)
            raise ValueError(f"Invalid planet '{raw}'. Allowed values: {allowed}.")

        if canonical not in seen:
            seen.add(canonical)
            normalized.append(canonical)

    return normalized


def _get_planet_signs(
    at_utc: datetime, planets: Sequence[str]
) -> dict[str, tuple[str, int]]:
    subject = AstrologicalSubjectFactory.from_iso_utc_time(
        name="Ingress Scan",
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

    signs: dict[str, tuple[str, int]] = {}
    for planet in planets:
        point = getattr(subject, planet.lower(), None)
        sign = getattr(point, "sign", None) if point is not None else None
        sign_num = getattr(point, "sign_num", None) if point is not None else None
        if sign is None or sign_num is None:
            raise KerykeionException(f"Unable to compute sign for planet '{planet}'.")
        signs[planet] = (str(sign), int(sign_num))

    return signs


def _refine_sign_ingress_time_utc(
    planet: str,
    low_utc: datetime,
    high_utc: datetime,
    previous_sign_num: int,
) -> tuple[datetime, str]:
    low_sign, low_sign_num = _get_planet_signs(low_utc, [planet])[planet]
    high_sign, high_sign_num = _get_planet_signs(high_utc, [planet])[planet]

    if low_sign_num != previous_sign_num:
        raise KerykeionException(
            f"Cannot refine ingress for {planet}: low bound sign changed unexpectedly ({low_sign})."
        )
    if high_sign_num == previous_sign_num:
        raise KerykeionException(
            f"Cannot refine ingress for {planet}: high bound does not cross sign boundary."
        )

    for _ in range(INGRESS_MAX_REFINEMENT_ITERATIONS):
        if high_utc - low_utc <= _REFINEMENT_DELTA:
            break

        mid_utc = low_utc + (high_utc - low_utc) / 2
        _, mid_sign_num = _get_planet_signs(mid_utc, [planet])[planet]

        if mid_sign_num == previous_sign_num:
            low_utc = mid_utc
            continue

        high_utc = mid_utc

    to_sign, _ = _get_planet_signs(high_utc, [planet])[planet]
    return high_utc, to_sign


def _build_period_events_for_planet(
    *,
    planet: str,
    start_utc: datetime,
    start_sign: str,
    transitions: list[dict],
) -> list[dict]:
    period_starts: list[dict] = [
        {
            "starts_at_utc": start_utc,
            "from_sign": None,
            "to_sign": start_sign,
        }
    ]

    for transition in transitions:
        transition_utc = transition["at_utc"]
        transition_from_sign = transition["from_sign"]
        transition_to_sign = transition["to_sign"]

        if transition_utc <= start_utc:
            period_starts[0]["from_sign"] = transition_from_sign
            period_starts[0]["to_sign"] = transition_to_sign
            continue

        period_starts.append(
            {
                "starts_at_utc": transition_utc,
                "from_sign": transition_from_sign,
                "to_sign": transition_to_sign,
            }
        )

    events: list[dict] = []
    for index, period in enumerate(period_starts):
        period_start_utc = period["starts_at_utc"]
        period_end_utc = None
        if index + 1 < len(period_starts):
            period_end_utc = period_starts[index + 1]["starts_at_utc"]

        events.append(
            {
                "event": "sign_ingress_period",
                "planet": planet,
                "starts_at_utc": period_start_utc.isoformat(),
                "ends_at_utc": period_end_utc.isoformat() if period_end_utc else None,
                "from_sign": period["from_sign"],
                "to_sign": period["to_sign"],
            }
        )

    return events


def compute_ingress_events(
    from_utc: datetime,
    horizon_days: int,
    planets: Sequence[str],
) -> list[dict]:
    if from_utc.tzinfo is None:
        raise KerykeionException("from_utc must include timezone information.")
    if horizon_days < 1:
        raise KerykeionException("horizon_days must be at least 1.")
    if horizon_days > INGRESS_MAX_HORIZON_DAYS:
        raise KerykeionException(
            f"horizon_days exceeds maximum allowed ({INGRESS_MAX_HORIZON_DAYS})."
        )

    normalized_planets = normalize_ingress_planets(planets)
    start_utc = from_utc.astimezone(timezone.utc)
    end_utc = start_utc + timedelta(days=horizon_days)

    transitions_by_planet: dict[str, list[dict]] = {
        planet: [] for planet in normalized_planets
    }
    previous_utc = start_utc
    previous_signs = _get_planet_signs(previous_utc, normalized_planets)
    start_signs = dict(previous_signs)

    while previous_utc < end_utc:
        current_utc = min(previous_utc + _COARSE_SCAN_DELTA, end_utc)
        current_signs = _get_planet_signs(current_utc, normalized_planets)

        for planet in normalized_planets:
            previous_sign, previous_sign_num = previous_signs[planet]
            current_sign, current_sign_num = current_signs[planet]

            if current_sign_num == previous_sign_num:
                continue

            event_utc, to_sign = _refine_sign_ingress_time_utc(
                planet=planet,
                low_utc=previous_utc,
                high_utc=current_utc,
                previous_sign_num=previous_sign_num,
            )
            if start_utc <= event_utc <= end_utc:
                transitions_by_planet[planet].append(
                    {
                        "at_utc": event_utc,
                        "from_sign": previous_sign,
                        "to_sign": to_sign,
                    }
                )

        previous_utc = current_utc
        previous_signs = current_signs

    events: list[dict] = []
    for planet in normalized_planets:
        start_sign = start_signs[planet][0]
        transitions = sorted(
            transitions_by_planet[planet], key=lambda item: item["at_utc"]
        )
        events.extend(
            _build_period_events_for_planet(
                planet=planet,
                start_utc=start_utc,
                start_sign=start_sign,
                transitions=transitions,
            )
        )

    events.sort(key=lambda event: (event["starts_at_utc"], event["planet"]))
    return events
