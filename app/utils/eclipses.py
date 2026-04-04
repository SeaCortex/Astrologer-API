from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Sequence

import swisseph as swe
from kerykeion.schemas import KerykeionException

ECLIPSE_ALLOWED_EVENT_TYPES: tuple[str, ...] = ("solar", "lunar")
ECLIPSE_DEFAULT_EVENT_TYPES: tuple[str, ...] = ("solar", "lunar")
ECLIPSE_ALLOWED_SOLAR_TYPES: tuple[str, ...] = ("total", "annular", "partial", "annular_total")
ECLIPSE_DEFAULT_SOLAR_TYPES: tuple[str, ...] = ("total", "annular", "partial", "annular_total")
ECLIPSE_ALLOWED_LUNAR_TYPES: tuple[str, ...] = ("total", "partial", "penumbral")
ECLIPSE_DEFAULT_LUNAR_TYPES: tuple[str, ...] = ("total", "partial", "penumbral")

ECLIPSE_MAX_HORIZON_DAYS = 3650
ECLIPSE_CURSOR_INCREMENT_MINUTES = 1

_EVENT_TYPE_LOOKUP: dict[str, str] = {value.lower(): value for value in ECLIPSE_ALLOWED_EVENT_TYPES}
_SOLAR_TYPE_LOOKUP: dict[str, str] = {value.lower(): value for value in ECLIPSE_ALLOWED_SOLAR_TYPES}
_LUNAR_TYPE_LOOKUP: dict[str, str] = {value.lower(): value for value in ECLIPSE_ALLOWED_LUNAR_TYPES}
_CURSOR_INCREMENT_DAYS = ECLIPSE_CURSOR_INCREMENT_MINUTES / 1440.0


def normalize_eclipse_event_types(event_types: Sequence[str]) -> list[str]:
    if not event_types:
        raise ValueError("event_types must contain at least one value.")

    normalized: list[str] = []
    seen: set[str] = set()

    for raw in event_types:
        if not isinstance(raw, str):
            raise ValueError("Each event type must be a string.")
        cleaned = raw.strip()
        if not cleaned:
            raise ValueError("Event type values cannot be empty.")

        canonical = _EVENT_TYPE_LOOKUP.get(cleaned.lower())
        if not canonical:
            allowed = ", ".join(ECLIPSE_ALLOWED_EVENT_TYPES)
            raise ValueError(f"Invalid event type '{raw}'. Allowed values: {allowed}.")

        if canonical not in seen:
            seen.add(canonical)
            normalized.append(canonical)

    return normalized


def normalize_solar_eclipse_types(solar_types: Sequence[str]) -> list[str]:
    if not solar_types:
        raise ValueError("solar_types must contain at least one value.")

    normalized: list[str] = []
    seen: set[str] = set()

    for raw in solar_types:
        if not isinstance(raw, str):
            raise ValueError("Each solar eclipse type must be a string.")
        cleaned = raw.strip()
        if not cleaned:
            raise ValueError("Solar eclipse type values cannot be empty.")

        canonical = _SOLAR_TYPE_LOOKUP.get(cleaned.lower())
        if not canonical:
            allowed = ", ".join(ECLIPSE_ALLOWED_SOLAR_TYPES)
            raise ValueError(f"Invalid solar eclipse type '{raw}'. Allowed values: {allowed}.")

        if canonical not in seen:
            seen.add(canonical)
            normalized.append(canonical)

    return normalized


def normalize_lunar_eclipse_types(lunar_types: Sequence[str]) -> list[str]:
    if not lunar_types:
        raise ValueError("lunar_types must contain at least one value.")

    normalized: list[str] = []
    seen: set[str] = set()

    for raw in lunar_types:
        if not isinstance(raw, str):
            raise ValueError("Each lunar eclipse type must be a string.")
        cleaned = raw.strip()
        if not cleaned:
            raise ValueError("Lunar eclipse type values cannot be empty.")

        canonical = _LUNAR_TYPE_LOOKUP.get(cleaned.lower())
        if not canonical:
            allowed = ", ".join(ECLIPSE_ALLOWED_LUNAR_TYPES)
            raise ValueError(f"Invalid lunar eclipse type '{raw}'. Allowed values: {allowed}.")

        if canonical not in seen:
            seen.add(canonical)
            normalized.append(canonical)

    return normalized


def _get_julian_day_utc(at_utc: datetime) -> float:
    at_utc = at_utc.astimezone(timezone.utc)
    utc_hour_decimal = (
        at_utc.hour
        + (at_utc.minute / 60.0)
        + (at_utc.second / 3600.0)
        + (at_utc.microsecond / 3_600_000_000.0)
    )
    return swe.julday(at_utc.year, at_utc.month, at_utc.day, utc_hour_decimal, swe.GREG_CAL)


def _jd_to_datetime_utc(jd_utc: float) -> datetime:
    year, month, day, hour = swe.revjul(jd_utc, swe.GREG_CAL)
    return datetime(year, month, day, tzinfo=timezone.utc) + timedelta(hours=hour)


def _jd_to_iso_utc(jd_utc: float) -> str:
    return _jd_to_datetime_utc(jd_utc).isoformat()


def _optional_jd_to_iso_utc(jd_utc: float) -> str | None:
    if jd_utc <= 0.0:
        return None
    return _jd_to_iso_utc(jd_utc)


def _decode_solar_type(retflags: int) -> str:
    if retflags & swe.ECL_ANNULAR_TOTAL:
        return "annular_total"
    if retflags & swe.ECL_TOTAL:
        return "total"
    if retflags & swe.ECL_ANNULAR:
        return "annular"
    if retflags & swe.ECL_PARTIAL:
        return "partial"
    raise KerykeionException(f"Unable to decode solar eclipse type from retflags={retflags}.")


def _decode_lunar_type(retflags: int) -> str:
    if retflags & swe.ECL_TOTAL:
        return "total"
    if retflags & swe.ECL_PARTIAL:
        return "partial"
    if retflags & swe.ECL_PENUMBRAL:
        return "penumbral"
    raise KerykeionException(f"Unable to decode lunar eclipse type from retflags={retflags}.")


def _compute_solar_events(*, start_jd: float, end_jd: float, selected_types: set[str]) -> list[dict]:
    events: list[dict] = []
    cursor_jd = start_jd

    while cursor_jd <= end_jd:
        retflags, tret = swe.sol_eclipse_when_glob(cursor_jd, swe.FLG_SWIEPH, swe.ECL_ALLTYPES_SOLAR)
        maximum_jd = float(tret[0])

        if maximum_jd > end_jd:
            break

        eclipse_type = _decode_solar_type(retflags)
        if eclipse_type in selected_types:
            where_retflags, geopos, attr = swe.sol_eclipse_where(maximum_jd, swe.FLG_SWIEPH)
            events.append(
                {
                    "event": "solar_eclipse",
                    "eclipse_type": eclipse_type,
                    "at_utc": _jd_to_iso_utc(maximum_jd),
                    "eclipse_begin_utc": _optional_jd_to_iso_utc(float(tret[2])),
                    "eclipse_end_utc": _optional_jd_to_iso_utc(float(tret[3])),
                    "totality_begin_utc": _optional_jd_to_iso_utc(float(tret[4])),
                    "totality_end_utc": _optional_jd_to_iso_utc(float(tret[5])),
                    "center_line_begin_utc": _optional_jd_to_iso_utc(float(tret[6])),
                    "center_line_end_utc": _optional_jd_to_iso_utc(float(tret[7])),
                    "annular_total_transition_utc": _optional_jd_to_iso_utc(float(tret[8])),
                    "annular_total_reversion_utc": _optional_jd_to_iso_utc(float(tret[9])),
                    "magnitude": float(attr[8]),
                    "obscuration": float(attr[2]),
                    "moon_to_sun_diameter_ratio": float(attr[1]),
                    "saros_series": None if float(attr[9]) < 0 else int(attr[9]),
                    "saros_member": None if float(attr[10]) < 0 else int(attr[10]),
                    "is_central": bool(where_retflags & swe.ECL_CENTRAL),
                    "is_noncentral": bool(where_retflags & swe.ECL_NONCENTRAL),
                    "greatest_eclipse_longitude": float(geopos[0]),
                    "greatest_eclipse_latitude": float(geopos[1]),
                }
            )

        # Move past this event to avoid repeating the same maximum instant.
        cursor_jd = max(maximum_jd + _CURSOR_INCREMENT_DAYS, cursor_jd + _CURSOR_INCREMENT_DAYS)

    return events


def _compute_lunar_events(*, start_jd: float, end_jd: float, selected_types: set[str]) -> list[dict]:
    events: list[dict] = []
    cursor_jd = start_jd

    while cursor_jd <= end_jd:
        retflags, tret = swe.lun_eclipse_when(cursor_jd, swe.FLG_SWIEPH, swe.ECL_ALLTYPES_LUNAR)
        maximum_jd = float(tret[0])

        if maximum_jd > end_jd:
            break

        eclipse_type = _decode_lunar_type(retflags)
        if eclipse_type in selected_types:
            # Magnitude and Saros values are global attributes; geopos affects only local az/alt fields.
            _, attr = swe.lun_eclipse_how(maximum_jd, (0.0, 0.0, 0.0), swe.FLG_SWIEPH)
            events.append(
                {
                    "event": "lunar_eclipse",
                    "eclipse_type": eclipse_type,
                    "at_utc": _jd_to_iso_utc(maximum_jd),
                    "eclipse_begin_utc": _optional_jd_to_iso_utc(float(tret[6])),
                    "eclipse_end_utc": _optional_jd_to_iso_utc(float(tret[7])),
                    "penumbral_begin_utc": _optional_jd_to_iso_utc(float(tret[6])),
                    "penumbral_end_utc": _optional_jd_to_iso_utc(float(tret[7])),
                    "partial_begin_utc": _optional_jd_to_iso_utc(float(tret[2])),
                    "partial_end_utc": _optional_jd_to_iso_utc(float(tret[3])),
                    "totality_begin_utc": _optional_jd_to_iso_utc(float(tret[4])),
                    "totality_end_utc": _optional_jd_to_iso_utc(float(tret[5])),
                    "magnitude": float(attr[8]),
                    "umbral_magnitude": float(attr[0]),
                    "penumbral_magnitude": float(attr[1]),
                    "saros_series": None if float(attr[9]) < 0 else int(attr[9]),
                    "saros_member": None if float(attr[10]) < 0 else int(attr[10]),
                }
            )

        cursor_jd = max(maximum_jd + _CURSOR_INCREMENT_DAYS, cursor_jd + _CURSOR_INCREMENT_DAYS)

    return events


def compute_eclipse_events(
    *,
    from_utc: datetime,
    horizon_days: int,
    event_types: Sequence[str],
    solar_types: Sequence[str],
    lunar_types: Sequence[str],
) -> list[dict]:
    if from_utc.tzinfo is None:
        raise KerykeionException("from_utc must include timezone information.")
    if horizon_days < 1:
        raise KerykeionException("horizon_days must be at least 1.")
    if horizon_days > ECLIPSE_MAX_HORIZON_DAYS:
        raise KerykeionException(
            f"horizon_days exceeds maximum allowed ({ECLIPSE_MAX_HORIZON_DAYS})."
        )

    normalized_event_types = normalize_eclipse_event_types(event_types)
    normalized_solar_types = normalize_solar_eclipse_types(solar_types)
    normalized_lunar_types = normalize_lunar_eclipse_types(lunar_types)

    start_utc = from_utc.astimezone(timezone.utc)
    end_utc = start_utc + timedelta(days=horizon_days)
    start_jd = _get_julian_day_utc(start_utc)
    end_jd = _get_julian_day_utc(end_utc)

    events: list[dict] = []
    if "solar" in normalized_event_types:
        events.extend(
            _compute_solar_events(
                start_jd=start_jd,
                end_jd=end_jd,
                selected_types=set(normalized_solar_types),
            )
        )
    if "lunar" in normalized_event_types:
        events.extend(
            _compute_lunar_events(
                start_jd=start_jd,
                end_jd=end_jd,
                selected_types=set(normalized_lunar_types),
            )
        )

    events.sort(key=lambda item: (item["at_utc"], item["event"]))
    return events
