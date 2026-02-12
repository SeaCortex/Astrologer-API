from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Callable, Optional, Sequence

from kerykeion import AstrologicalSubjectFactory
from kerykeion.schemas import KerykeionException
from kerykeion.schemas.kr_models import AstrologicalSubjectModel

SECONDS_PER_DAY = 86400.0
TROPICAL_YEAR_DAYS = 365.2425
INGRESS_REFINEMENT_SECONDS = 60

PROGRESSED_PHASES = (
    (90.0, "New Moon"),
    (180.0, "First Quarter"),
    (270.0, "Full Moon"),
    (360.0, "Last Quarter"),
)


def parse_iso_utc(value: str) -> datetime:
    try:
        dt = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise KerykeionException(f"Invalid ISO datetime: {value}") from exc
    if dt.tzinfo is None:
        raise KerykeionException(f"Timezone offset is required: {value}")
    return dt.astimezone(timezone.utc)


def ensure_progressed_points(active_points: Optional[Sequence[str]]) -> list[str]:
    resolved = list(active_points) if active_points else []
    existing = {point.lower() for point in resolved}
    for required in ("Sun", "Moon"):
        if required.lower() not in existing:
            resolved.append(required)
    return resolved


def wrap360(value: float) -> float:
    return value % 360.0


def calculate_progressed_datetime(birth_utc: datetime, target_utc: datetime) -> datetime:
    age_days = (target_utc - birth_utc).total_seconds() / SECONDS_PER_DAY
    progressed_days = age_days / TROPICAL_YEAR_DAYS
    return birth_utc + timedelta(days=progressed_days)


def _phase_name_from_angle(angle_deg: float) -> str:
    for threshold, name in PROGRESSED_PHASES:
        if angle_deg < threshold:
            return name
    return "Last Quarter"


def _build_progressed_subject(
    natal_subject: AstrologicalSubjectModel,
    progressed_utc: datetime,
    active_points: list[str],
) -> AstrologicalSubjectModel:
    return AstrologicalSubjectFactory.from_iso_utc_time(
        name=f"{natal_subject.name} Progressed",
        iso_utc_time=progressed_utc.isoformat(),
        city=natal_subject.city,
        nation=natal_subject.nation,
        tz_str=natal_subject.tz_str,
        online=False,
        lng=natal_subject.lng,
        lat=natal_subject.lat,
        zodiac_type=natal_subject.zodiac_type,
        sidereal_mode=natal_subject.sidereal_mode,
        houses_system_identifier=natal_subject.houses_system_identifier,
        perspective_type=natal_subject.perspective_type,
        active_points=active_points,
        suppress_geonames_warning=True,
    )


def _refine_ingress(
    low_target: datetime,
    high_target: datetime,
    previous_value: str,
    value_getter: Callable[[AstrologicalSubjectModel], str],
    evaluate: Callable[[datetime], tuple[datetime, AstrologicalSubjectModel]],
) -> tuple[datetime, datetime, str]:
    high_progressed, high_subject = evaluate(high_target)
    high_value = value_getter(high_subject)

    while (high_target - low_target).total_seconds() > INGRESS_REFINEMENT_SECONDS:
        mid_target = low_target + (high_target - low_target) / 2
        mid_progressed, mid_subject = evaluate(mid_target)
        mid_value = value_getter(mid_subject)

        if mid_value == previous_value:
            low_target = mid_target
            continue

        high_target = mid_target
        high_progressed = mid_progressed
        high_value = mid_value

    return high_target, high_progressed, high_value


def compute_progressed_moon_cycle(
    natal_subject: AstrologicalSubjectModel,
    target_iso_datetime: str,
    range_end_iso_datetime: str,
    step_days: int,
    active_points: Optional[Sequence[str]] = None,
) -> dict:
    target_utc = parse_iso_utc(target_iso_datetime)
    range_end_utc = parse_iso_utc(range_end_iso_datetime)
    if range_end_utc <= target_utc:
        raise KerykeionException("range_end_iso_datetime must be later than target_iso_datetime.")

    birth_utc = parse_iso_utc(natal_subject.iso_formatted_utc_datetime)
    effective_active_points = ensure_progressed_points(active_points or natal_subject.active_points)

    cache: dict[datetime, tuple[datetime, AstrologicalSubjectModel]] = {}

    def evaluate(target_dt: datetime) -> tuple[datetime, AstrologicalSubjectModel]:
        cached = cache.get(target_dt)
        if cached is not None:
            return cached
        progressed_utc = calculate_progressed_datetime(birth_utc, target_dt)
        progressed_subject = _build_progressed_subject(
            natal_subject=natal_subject,
            progressed_utc=progressed_utc,
            active_points=effective_active_points,
        )
        result = (progressed_utc, progressed_subject)
        cache[target_dt] = result
        return result

    progressed_utc, progressed_subject = evaluate(target_utc)
    if progressed_subject.sun is None or progressed_subject.moon is None:
        raise KerykeionException("Sun and Moon are required for progressed moon cycle calculation.")

    lunation_angle = wrap360(progressed_subject.moon.abs_pos - progressed_subject.sun.abs_pos)
    lunation_phase = _phase_name_from_angle(lunation_angle)

    current_target = target_utc
    current_subject = progressed_subject

    if current_subject.moon is None:
        raise KerykeionException("Moon is required for progressed ingress detection.")

    current_sign = current_subject.moon.sign
    current_house = current_subject.moon.house
    next_sign_ingress = None
    next_house_ingress = None

    while current_target < range_end_utc and (next_sign_ingress is None or next_house_ingress is None):
        next_target = min(current_target + timedelta(days=step_days), range_end_utc)
        next_progressed_utc, next_subject = evaluate(next_target)

        if next_subject.moon is None:
            raise KerykeionException("Moon is required for progressed ingress detection.")

        if next_sign_ingress is None and next_subject.moon.sign != current_sign:
            ingress_target, ingress_progressed, sign_value = _refine_ingress(
                low_target=current_target,
                high_target=next_target,
                previous_value=str(current_sign),
                value_getter=lambda subject: str(subject.moon.sign if subject.moon else ""),
                evaluate=evaluate,
            )
            next_sign_ingress = {
                "at_target_iso_datetime": ingress_target.isoformat(),
                "at_progressed_iso_datetime": ingress_progressed.isoformat(),
                "sign": sign_value,
            }

        if next_house_ingress is None and next_subject.moon.house != current_house:
            ingress_target, ingress_progressed, house_value = _refine_ingress(
                low_target=current_target,
                high_target=next_target,
                previous_value=str(current_house),
                value_getter=lambda subject: str(subject.moon.house if subject.moon else ""),
                evaluate=evaluate,
            )
            next_house_ingress = {
                "at_target_iso_datetime": ingress_target.isoformat(),
                "at_progressed_iso_datetime": ingress_progressed.isoformat(),
                "house": house_value,
            }

        current_target = next_target
        current_subject = next_subject
        current_sign = current_subject.moon.sign
        current_house = current_subject.moon.house

    return {
        "target_iso_datetime": target_utc.isoformat(),
        "progressed_iso_datetime": progressed_utc.isoformat(),
        "progressed_subject": progressed_subject,
        "progressed_lunation": {
            "angle_deg": round(lunation_angle, 6),
            "phase_name": lunation_phase,
        },
        "next_ingresses": {
            "next_sign_ingress": next_sign_ingress,
            "next_house_ingress": next_house_ingress,
        },
    }
