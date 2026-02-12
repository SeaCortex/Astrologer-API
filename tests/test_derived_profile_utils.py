from __future__ import annotations

from kerykeion import AstrologicalSubjectFactory

from app.utils.derived_profile import (
    compute_chart_ruler,
    compute_hemispheric_emphasis,
    compute_lunar_mansion,
    compute_stelliums,
)


def _build_subject():
    return AstrologicalSubjectFactory.from_birth_data(
        name="Derived Utils",
        year=1991,
        month=4,
        day=2,
        hour=14,
        minute=25,
        city="Rome",
        nation="IT",
        lng=12.4964,
        lat=41.9028,
        tz_str="Europe/Rome",
        online=False,
        suppress_geonames_warning=True,
    )


def _circular_diff(a: float, b: float) -> float:
    diff = abs(a - b)
    if diff > 180:
        diff = 360 - diff
    return diff


def test_chart_ruler_matches_ascendant_sign_mapping():
    subject = _build_subject()
    chart_ruler = compute_chart_ruler(subject)

    traditional = {
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

    assert chart_ruler["asc_sign"] == subject.ascendant.sign
    assert chart_ruler["ruler_point_name"] == traditional[subject.ascendant.sign]
    assert chart_ruler["ruler_point"] is not None


def test_stelliums_respect_active_points_filter():
    subject = _build_subject()
    filtered = compute_stelliums(subject, active_points=["Sun", "Moon"])
    assert filtered["by_sign"] == []
    assert filtered["by_house"] == []
    assert filtered["min_count"] == 3


def test_hemisphere_counts_and_percentages_are_consistent():
    subject = _build_subject()
    hemispheres = compute_hemispheric_emphasis(subject)

    above_below = hemispheres["above_below_horizon"]
    east_west = hemispheres["east_west"]

    above_total = above_below["above_count"] + above_below["below_count"]
    east_total = east_west["east_count"] + east_west["west_count"]
    counted = len(above_below["counted_points"])

    assert above_total == counted
    assert east_total == counted

    if counted:
        assert _circular_diff(above_below["above_pct"] + above_below["below_pct"], 100.0) <= 0.1
        assert _circular_diff(east_west["east_pct"] + east_west["west_pct"], 100.0) <= 0.1


def test_lunar_mansion_range_is_valid():
    subject = _build_subject()
    lunar_mansion = compute_lunar_mansion(subject)

    assert 1 <= lunar_mansion["index"] <= 28
    assert lunar_mansion["system"] == "tropical_28_equal"
    assert lunar_mansion["start_abs_deg"] <= lunar_mansion["moon_abs_pos"] < lunar_mansion["end_abs_deg"]
    assert abs((lunar_mansion["end_abs_deg"] - lunar_mansion["start_abs_deg"]) - (360.0 / 28.0)) < 1e-9
