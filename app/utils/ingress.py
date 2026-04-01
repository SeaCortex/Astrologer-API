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

_PLANET_LOOKUP: dict[str, str] = {planet.lower(): planet for planet in INGRESS_ALLOWED_PLANETS}
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


def _get_planet_signs(at_utc: datetime, planets: Sequence[str]) -> dict[str, tuple[str, int]]:
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

    events: list[dict] = []
    previous_utc = start_utc
    previous_signs = _get_planet_signs(previous_utc, normalized_planets)

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
                events.append(
                    {
                        "event": "sign_ingress",
                        "planet": planet,
                        "at_utc": event_utc.isoformat(),
                        "from_sign": previous_sign,
                        "to_sign": to_sign,
                    }
                )

            # Keep progression aligned with coarse snapshot state.
            previous_signs[planet] = (current_sign, current_sign_num)

        previous_utc = current_utc
        previous_signs = current_signs

    events.sort(key=lambda event: (event["at_utc"], event["planet"]))
    return events
