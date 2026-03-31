from __future__ import annotations

import math
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Final

import swisseph as swe
from kerykeion import AstrologicalSubjectFactory
from kerykeion.schemas import KerykeionException

LUNAR_PHASE_EVENTS_MAX_HORIZON_DAYS = 1826
LUNAR_EVENTS_COARSE_SCAN_STEP_HOURS = 6
LUNAR_EVENTS_REFINEMENT_STEP_MINUTES = 1
LUNAR_EVENTS_MAX_REFINEMENT_ITERATIONS = 64
LUNAR_DISTANCE_COARSE_SCAN_STEP_HOURS = 3
LUNAR_DISTANCE_SCAN_MARGIN_DAYS = 35
LUNAR_AU_TO_KM = 149_597_870.7
LUNAR_SUPER_LUNA_NOLLE_THRESHOLD_PCT = 90.0
LUNAR_SUPER_LUNA_DEFAULT_DISTANCE_KM_THRESHOLD = 360_000.0

LUNAR_EVENT_TARGETS: Final[tuple[tuple[str, float], ...]] = (
    ("new_moon", 0.0),
    ("first_quarter", 90.0),
    ("full_moon", 180.0),
    ("last_quarter", 270.0),
)

_COARSE_SCAN_DELTA = timedelta(hours=LUNAR_EVENTS_COARSE_SCAN_STEP_HOURS)
_REFINEMENT_DELTA = timedelta(minutes=LUNAR_EVENTS_REFINEMENT_STEP_MINUTES)
_DISTANCE_SCAN_DELTA = timedelta(hours=LUNAR_DISTANCE_COARSE_SCAN_STEP_HOURS)
_EXTREMUM_DEDUPE_WINDOW = timedelta(hours=6)
_SLOPE_EPSILON_AU = 1e-10


@dataclass(frozen=True)
class LunarDistanceExtremum:
    kind: str
    at_utc: datetime
    distance_au: float

    @property
    def distance_km(self) -> float:
        return self.distance_au * LUNAR_AU_TO_KM


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


def _get_julian_day_utc(at_utc: datetime) -> float:
    at_utc = at_utc.astimezone(timezone.utc)
    utc_hour_decimal = (
        at_utc.hour
        + (at_utc.minute / 60.0)
        + (at_utc.second / 3600.0)
        + (at_utc.microsecond / 3_600_000_000.0)
    )
    return swe.julday(at_utc.year, at_utc.month, at_utc.day, utc_hour_decimal, swe.GREG_CAL)


def _get_moon_distance_au_utc(at_utc: datetime) -> float:
    moon_calc = swe.calc_ut(_get_julian_day_utc(at_utc), swe.MOON, swe.FLG_SWIEPH)[0]
    return float(moon_calc[2])


def _refine_distance_extremum_utc(low_utc: datetime, high_utc: datetime, *, kind: str) -> LunarDistanceExtremum:
    if kind not in {"perigee", "apogee"}:
        raise KerykeionException(f"Unsupported extremum kind: {kind}")

    for _ in range(LUNAR_EVENTS_MAX_REFINEMENT_ITERATIONS):
        if high_utc - low_utc <= _REFINEMENT_DELTA:
            break

        third = (high_utc - low_utc) / 3
        mid_one = low_utc + third
        mid_two = high_utc - third
        dist_one = _get_moon_distance_au_utc(mid_one)
        dist_two = _get_moon_distance_au_utc(mid_two)

        if kind == "perigee":
            if dist_one <= dist_two:
                high_utc = mid_two
            else:
                low_utc = mid_one
            continue

        if dist_one >= dist_two:
            high_utc = mid_two
        else:
            low_utc = mid_one

    extremum_utc = low_utc + ((high_utc - low_utc) / 2)
    return LunarDistanceExtremum(
        kind=kind,
        at_utc=extremum_utc,
        distance_au=_get_moon_distance_au_utc(extremum_utc),
    )


def _dedupe_extrema(extrema: list[LunarDistanceExtremum], *, kind: str) -> list[LunarDistanceExtremum]:
    if not extrema:
        return []

    sorted_extrema = sorted(extrema, key=lambda item: item.at_utc)
    deduped: list[LunarDistanceExtremum] = []

    for candidate in sorted_extrema:
        if not deduped:
            deduped.append(candidate)
            continue

        previous = deduped[-1]
        if candidate.at_utc - previous.at_utc > _EXTREMUM_DEDUPE_WINDOW:
            deduped.append(candidate)
            continue

        if kind == "perigee":
            deduped[-1] = candidate if candidate.distance_au < previous.distance_au else previous
        else:
            deduped[-1] = candidate if candidate.distance_au > previous.distance_au else previous

    return deduped


def _scan_lunar_distance_extrema(from_utc: datetime, to_utc: datetime) -> tuple[list[LunarDistanceExtremum], list[LunarDistanceExtremum]]:
    timestamps: list[datetime] = []
    distances: list[float] = []

    cursor_utc = from_utc
    while cursor_utc <= to_utc:
        timestamps.append(cursor_utc)
        distances.append(_get_moon_distance_au_utc(cursor_utc))
        cursor_utc += _DISTANCE_SCAN_DELTA

    if not timestamps or timestamps[-1] < to_utc:
        timestamps.append(to_utc)
        distances.append(_get_moon_distance_au_utc(to_utc))

    perigees: list[LunarDistanceExtremum] = []
    apogees: list[LunarDistanceExtremum] = []

    for idx in range(1, len(timestamps) - 1):
        slope_left = distances[idx] - distances[idx - 1]
        slope_right = distances[idx + 1] - distances[idx]
        bracket_low = timestamps[idx - 1]
        bracket_high = timestamps[idx + 1]

        if slope_left < -_SLOPE_EPSILON_AU and slope_right > _SLOPE_EPSILON_AU:
            perigees.append(_refine_distance_extremum_utc(bracket_low, bracket_high, kind="perigee"))
            continue

        if slope_left > _SLOPE_EPSILON_AU and slope_right < -_SLOPE_EPSILON_AU:
            apogees.append(_refine_distance_extremum_utc(bracket_low, bracket_high, kind="apogee"))

    return (
        _dedupe_extrema(perigees, kind="perigee"),
        _dedupe_extrema(apogees, kind="apogee"),
    )


def _nearest_extremum(at_utc: datetime, extrema: list[LunarDistanceExtremum]) -> LunarDistanceExtremum | None:
    if not extrema:
        return None
    return min(extrema, key=lambda item: abs(item.at_utc - at_utc))


def _previous_and_next_perigee(
    at_utc: datetime, perigees: list[LunarDistanceExtremum]
) -> tuple[LunarDistanceExtremum | None, LunarDistanceExtremum | None]:
    previous = None
    following = None

    for candidate in perigees:
        if candidate.at_utc <= at_utc:
            previous = candidate
            continue
        following = candidate
        break

    return previous, following


def _apogee_in_cycle(
    start_perigee_utc: datetime,
    end_perigee_utc: datetime,
    apogees: list[LunarDistanceExtremum],
) -> LunarDistanceExtremum | None:
    cycle_apogees = [item for item in apogees if start_perigee_utc < item.at_utc <= end_perigee_utc]
    if not cycle_apogees:
        return None
    return cycle_apogees[0]


def _augment_events_with_distance_metrics(
    *,
    events: list[dict],
    start_utc: datetime,
    end_utc: datetime,
    include_super_luna: bool,
    super_luna_definition: str,
    super_luna_distance_km_threshold: float,
) -> None:
    if not events:
        return

    extrema_scan_start = start_utc - timedelta(days=LUNAR_DISTANCE_SCAN_MARGIN_DAYS)
    extrema_scan_end = end_utc + timedelta(days=LUNAR_DISTANCE_SCAN_MARGIN_DAYS)
    perigees, apogees = _scan_lunar_distance_extrema(extrema_scan_start, extrema_scan_end)

    for item in events:
        event_utc = datetime.fromisoformat(item["at_utc"]).astimezone(timezone.utc)
        event_distance_au = _get_moon_distance_au_utc(event_utc)
        event_distance_km = event_distance_au * LUNAR_AU_TO_KM

        item["moon_distance_au"] = event_distance_au
        item["moon_distance_km"] = event_distance_km

        nearest_perigee = _nearest_extremum(event_utc, perigees)
        nearest_apogee = _nearest_extremum(event_utc, apogees)

        if nearest_perigee is not None:
            item["nearest_perigee_utc"] = nearest_perigee.at_utc.isoformat()
            item["nearest_perigee_km"] = nearest_perigee.distance_km
            item["delta_to_perigee_hours"] = abs((event_utc - nearest_perigee.at_utc).total_seconds()) / 3600.0

        if nearest_apogee is not None:
            item["nearest_apogee_utc"] = nearest_apogee.at_utc.isoformat()
            item["nearest_apogee_km"] = nearest_apogee.distance_km

        previous_perigee, next_perigee = _previous_and_next_perigee(event_utc, perigees)
        cycle_apogee = (
            _apogee_in_cycle(previous_perigee.at_utc, next_perigee.at_utc, apogees)
            if previous_perigee and next_perigee
            else None
        )

        closeness_pct = None
        if previous_perigee and next_perigee and cycle_apogee:
            cycle_perigee = (
                previous_perigee
                if abs(event_utc - previous_perigee.at_utc) <= abs(next_perigee.at_utc - event_utc)
                else next_perigee
            )

            denominator_km = cycle_apogee.distance_km - cycle_perigee.distance_km
            if denominator_km > 0:
                closeness_pct = ((cycle_apogee.distance_km - event_distance_km) / denominator_km) * 100.0
                closeness_pct = max(0.0, min(100.0, closeness_pct))
                item["anomalistic_closeness_pct"] = closeness_pct

        if not include_super_luna:
            continue

        is_candidate = item["event"] in {"new_moon", "full_moon"}
        item["is_super_luna_candidate"] = is_candidate

        if not is_candidate:
            item["is_super_luna"] = False
            continue

        if super_luna_definition == "distance_threshold_km":
            item["is_super_luna"] = event_distance_km <= super_luna_distance_km_threshold
            continue

        item["is_super_luna"] = (
            (closeness_pct is not None) and (closeness_pct >= LUNAR_SUPER_LUNA_NOLLE_THRESHOLD_PCT)
        )


def compute_lunar_phase_events(
    *,
    from_utc: datetime,
    horizon_days: int,
    include_distance_metrics: bool = False,
    include_super_luna: bool = False,
    super_luna_definition: str = "nolle_90pct_cycle",
    super_luna_distance_km_threshold: float = LUNAR_SUPER_LUNA_DEFAULT_DISTANCE_KM_THRESHOLD,
) -> dict:
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

    include_distance_data = include_distance_metrics or include_super_luna
    if include_distance_data:
        _augment_events_with_distance_metrics(
            events=events,
            start_utc=start_utc,
            end_utc=end_utc,
            include_super_luna=include_super_luna,
            super_luna_definition=super_luna_definition,
            super_luna_distance_km_threshold=super_luna_distance_km_threshold,
        )

    events.sort(key=lambda event: event["at_utc"])

    payload: dict = {"events": events}
    if include_distance_data:
        payload["distance_frame"] = "geocentric"
        payload["distance_units"] = ["au", "km"]
    if include_super_luna:
        payload["super_luna_definition_applied"] = super_luna_definition
        if super_luna_definition == "distance_threshold_km":
            payload["super_luna_distance_km_threshold_applied"] = super_luna_distance_km_threshold

    return payload
