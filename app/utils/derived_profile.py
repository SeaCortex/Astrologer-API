from __future__ import annotations

from collections import defaultdict
from typing import Optional, Sequence

from kerykeion.schemas import KerykeionException
from kerykeion.schemas.kr_models import AstrologicalSubjectModel, KerykeionPointModel

TRADITIONAL_STELLIUM_POINTS: tuple[str, ...] = (
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

POINT_ATTR_BY_NAME: dict[str, str] = {
    "Sun": "sun",
    "Moon": "moon",
    "Mercury": "mercury",
    "Venus": "venus",
    "Mars": "mars",
    "Jupiter": "jupiter",
    "Saturn": "saturn",
    "Uranus": "uranus",
    "Neptune": "neptune",
    "Pluto": "pluto",
}

HOUSE_NUMBER_BY_NAME: dict[str, int] = {
    "First_House": 1,
    "Second_House": 2,
    "Third_House": 3,
    "Fourth_House": 4,
    "Fifth_House": 5,
    "Sixth_House": 6,
    "Seventh_House": 7,
    "Eighth_House": 8,
    "Ninth_House": 9,
    "Tenth_House": 10,
    "Eleventh_House": 11,
    "Twelfth_House": 12,
}

SIGN_ORDER: dict[str, int] = {
    "Ari": 0,
    "Tau": 1,
    "Gem": 2,
    "Can": 3,
    "Leo": 4,
    "Vir": 5,
    "Lib": 6,
    "Sco": 7,
    "Sag": 8,
    "Cap": 9,
    "Aqu": 10,
    "Pis": 11,
}

TRADITIONAL_CHART_RULERS: dict[str, str] = {
    "Ari": "Mars",
    "Tau": "Venus",
    "Gem": "Mercury",
    "Can": "Moon",
    "Leo": "Sun",
    "Vir": "Mercury",
    "Lib": "Venus",
    "Sco": "Mars",
    "Sag": "Jupiter",
    "Cap": "Saturn",
    "Aqu": "Saturn",
    "Pis": "Jupiter",
}

LUNAR_MANSION_SYSTEM = "tropical_28_equal"
LUNAR_MANSION_COUNT = 28
LUNAR_MANSION_WIDTH = 360.0 / LUNAR_MANSION_COUNT

REQUIRED_DERIVED_ACTIVE_POINTS: tuple[str, ...] = (
    "Ascendant",
    "Moon",
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


def ensure_required_derived_points(active_points: Sequence[str]) -> list[str]:
    resolved = list(active_points)
    existing = {point.lower() for point in resolved}
    for point in REQUIRED_DERIVED_ACTIVE_POINTS:
        if point.lower() not in existing:
            resolved.append(point)
    return resolved


def _eligible_point_names(active_points: Optional[Sequence[str]]) -> list[str]:
    if not active_points:
        return list(TRADITIONAL_STELLIUM_POINTS)

    active_set = {point.lower() for point in active_points}
    return [point for point in TRADITIONAL_STELLIUM_POINTS if point.lower() in active_set]


def _resolve_point(subject: AstrologicalSubjectModel, point_name: str) -> Optional[KerykeionPointModel]:
    attr = POINT_ATTR_BY_NAME[point_name]
    point = getattr(subject, attr, None)
    if isinstance(point, KerykeionPointModel):
        return point
    return None


def _house_number(house_name: Optional[str]) -> Optional[int]:
    if house_name is None:
        return None
    return HOUSE_NUMBER_BY_NAME.get(str(house_name))


def compute_chart_ruler(subject: AstrologicalSubjectModel) -> dict:
    ascendant = subject.ascendant
    if ascendant is None:
        raise KerykeionException("Ascendant is required to compute chart ruler.")

    asc_sign = ascendant.sign
    ruler_name = TRADITIONAL_CHART_RULERS.get(asc_sign)
    if ruler_name is None:
        raise KerykeionException(f"Unsupported ascendant sign for chart ruler: {asc_sign}")

    ruler_attr = POINT_ATTR_BY_NAME[ruler_name]
    ruler_point = getattr(subject, ruler_attr, None)

    return {
        "asc_sign": asc_sign,
        "ruler_point_name": ruler_name,
        "ruler_point": ruler_point,
    }


def compute_stelliums(
    subject: AstrologicalSubjectModel,
    active_points: Optional[Sequence[str]] = None,
    min_count: int = 3,
) -> dict:
    by_sign: dict[str, list[str]] = defaultdict(list)
    by_house: dict[str, list[str]] = defaultdict(list)

    for point_name in _eligible_point_names(active_points):
        point = _resolve_point(subject, point_name)
        if point is None:
            continue
        by_sign[str(point.sign)].append(point_name)
        if point.house is not None:
            by_house[str(point.house)].append(point_name)

    sign_items = [
        {"sign": sign, "points": sorted(points)}
        for sign, points in by_sign.items()
        if len(points) >= min_count
    ]
    sign_items.sort(key=lambda item: SIGN_ORDER.get(item["sign"], 999))

    house_items = [
        {"house": house, "points": sorted(points)}
        for house, points in by_house.items()
        if len(points) >= min_count
    ]
    house_items.sort(key=lambda item: HOUSE_NUMBER_BY_NAME.get(item["house"], 999))

    return {
        "min_count": min_count,
        "by_sign": sign_items,
        "by_house": house_items,
    }


def _percentage(count: int, total: int) -> float:
    if total == 0:
        return 0.0
    return round((count / total) * 100.0, 2)


def compute_hemispheric_emphasis(
    subject: AstrologicalSubjectModel,
    active_points: Optional[Sequence[str]] = None,
) -> dict:
    eligible_points: list[str] = []
    above_count = 0
    below_count = 0
    east_count = 0
    west_count = 0

    for point_name in _eligible_point_names(active_points):
        point = _resolve_point(subject, point_name)
        if point is None:
            continue

        house_number = _house_number(point.house)
        if house_number is None:
            continue

        eligible_points.append(point_name)

        if house_number >= 7:
            above_count += 1
        else:
            below_count += 1

        if house_number in {10, 11, 12, 1, 2, 3}:
            east_count += 1
        else:
            west_count += 1

    total = len(eligible_points)
    return {
        "above_below_horizon": {
            "above_count": above_count,
            "below_count": below_count,
            "above_pct": _percentage(above_count, total),
            "below_pct": _percentage(below_count, total),
            "counted_points": eligible_points,
        },
        "east_west": {
            "east_count": east_count,
            "west_count": west_count,
            "east_pct": _percentage(east_count, total),
            "west_pct": _percentage(west_count, total),
            "counted_points": eligible_points,
        },
    }


def compute_lunar_mansion(subject: AstrologicalSubjectModel) -> dict:
    moon = subject.moon
    if moon is None:
        raise KerykeionException("Moon is required to compute lunar mansion.")

    moon_abs_pos = moon.abs_pos % 360.0
    index = int(moon_abs_pos // LUNAR_MANSION_WIDTH) + 1
    start_abs_deg = (index - 1) * LUNAR_MANSION_WIDTH
    end_abs_deg = start_abs_deg + LUNAR_MANSION_WIDTH

    return {
        "system": LUNAR_MANSION_SYSTEM,
        "index": index,
        "start_abs_deg": start_abs_deg,
        "end_abs_deg": end_abs_deg,
        "moon_abs_pos": moon_abs_pos,
    }


def build_derived_natal_profile(
    subject: AstrologicalSubjectModel,
    active_points: Optional[Sequence[str]] = None,
) -> dict:
    return {
        "chart_ruler": compute_chart_ruler(subject),
        "stelliums": compute_stelliums(subject, active_points=active_points),
        "hemispheres": compute_hemispheric_emphasis(subject, active_points=active_points),
        "lunar_mansion": compute_lunar_mansion(subject),
    }
