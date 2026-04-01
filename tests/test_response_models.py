"""
Unit test per i modelli di risposta che sfruttano direttamente le strutture
Pydantic fornite da kerykeion. Verifichiamo che i payload generati dalle factory
native vengano accettati e tipizzati correttamente.
"""

from __future__ import annotations

from typing import Iterable

import pytest

from kerykeion import AstrologicalSubjectFactory, ChartDataFactory
from kerykeion.schemas.kr_models import (
    AstrologicalSubjectModel,
    DualChartDataModel,
    RelationshipScoreAspectModel,
    SingleChartDataModel,
    ScoreBreakdownItemModel,
)
from kerykeion.settings.config_constants import DEFAULT_ACTIVE_ASPECTS, DEFAULT_ACTIVE_POINTS

from app.types import response_models as rm


def _active_aspects_payload() -> list[dict]:
    """Replica la trasformazione applicata dal router principale."""
    return [dict(aspect) for aspect in DEFAULT_ACTIVE_ASPECTS]


def _active_points_payload(points: Iterable[str] | None = None) -> list[str]:
    if points:
        return list(points)
    return list(DEFAULT_ACTIVE_POINTS)


def _build_subject(name: str, *, year: int, month: int, day: int, hour: int, minute: int, city: str, lat: float, lng: float) -> object:
    """Crea un soggetto astrologico inattivo (offline)."""
    return AstrologicalSubjectFactory.from_birth_data(
        name=name,
        year=year,
        month=month,
        day=day,
        hour=hour,
        minute=minute,
        seconds=0,
        city=city,
        nation="IT",
        lng=lng,
        lat=lat,
        tz_str="Europe/Rome",
        online=False,
        active_points=_active_points_payload(),
        suppress_geonames_warning=True,
    )


@pytest.fixture(scope="module")
def single_chart_dump() -> dict:
    subject = _build_subject("Giulia", year=1990, month=1, day=1, hour=12, minute=30, city="Rome", lat=41.9, lng=12.5)
    chart_data = ChartDataFactory.create_natal_chart_data(
        subject,
        active_points=_active_points_payload(),
        active_aspects=_active_aspects_payload(),
    )
    return chart_data.model_dump(mode="json")


@pytest.fixture(scope="module")
def dual_chart_dump() -> dict:
    first = _build_subject("Marco", year=1988, month=5, day=10, hour=10, minute=10, city="Florence", lat=43.77, lng=11.25)
    second = _build_subject("Lucia", year=1992, month=9, day=25, hour=8, minute=5, city="Milan", lat=45.46, lng=9.19)
    chart_data = ChartDataFactory.create_synastry_chart_data(
        first,
        second,
        active_points=_active_points_payload(),
        active_aspects=_active_aspects_payload(),
        include_relationship_score=True,
        include_house_comparison=True,
    )
    return chart_data.model_dump(mode="json")


def test_status_response_model_accepts_minimal_payload():
    payload = {"status": "OK"}
    model = rm.StatusResponseModel.model_validate(payload)
    assert model.status == "OK"


def test_api_status_response_model_includes_environment_flags():
    payload = {"status": "OK", "environment": "test", "debug": True}
    model = rm.ApiStatusResponseModel.model_validate(payload)
    assert model.environment == "test"
    assert model.debug is True


def test_subject_response_model_parses_subject_dict(single_chart_dump: dict):
    subject_payload = single_chart_dump["subject"]
    model = rm.SubjectResponseModel.model_validate({"status": "OK", "subject": subject_payload})
    assert isinstance(model.subject, AstrologicalSubjectModel)
    assert model.subject.name == "Giulia"


def test_chart_data_response_model_accepts_single_chart(single_chart_dump: dict):
    payload = {"status": "OK", "chart_data": single_chart_dump}
    model = rm.ChartDataResponseModel.model_validate(payload)
    assert isinstance(model.chart_data, SingleChartDataModel)
    assert model.chart_data.chart_type == "Natal"


def test_chart_response_model_accepts_single_chart_with_svg(single_chart_dump: dict):
    payload = {
        "status": "OK",
        "chart_data": single_chart_dump,
        "chart": "<svg>mock</svg>",
    }
    model = rm.ChartResponseModel.model_validate(payload)
    assert isinstance(model.chart_data, SingleChartDataModel)
    assert model.chart == "<svg>mock</svg>"
    assert model.chart_wheel is None
    assert model.chart_grid is None


def test_chart_response_model_handles_split_variant(single_chart_dump: dict):
    payload = {
        "status": "OK",
        "chart_data": single_chart_dump,
        "chart_wheel": "<svg>wheel</svg>",
        "chart_grid": "<svg>grid</svg>",
    }
    model = rm.ChartResponseModel.model_validate(payload)
    assert isinstance(model.chart_data, SingleChartDataModel)
    assert model.chart is None
    assert model.chart_wheel == "<svg>wheel</svg>"
    assert model.chart_grid == "<svg>grid</svg>"


def test_return_chart_response_model_extends_chart_payload(single_chart_dump: dict):
    payload = {
        "status": "OK",
        "chart_data": single_chart_dump,
        "chart": "<svg>return</svg>",
        "return_type": "Solar",
        "wheel_type": "dual",
    }
    model = rm.ReturnChartResponseModel.model_validate(payload)
    assert isinstance(model.chart_data, SingleChartDataModel)
    assert model.return_type == "Solar"
    assert model.wheel_type == "dual"


def test_compatibility_score_response_model_parses_dual_chart(dual_chart_dump: dict):
    relationship_score = dual_chart_dump.get("relationship_score")
    assert relationship_score, "Relationship score atteso nei payload di synastry"

    aspects_dump = relationship_score["aspects"]
    payload = {
        "status": "OK",
        "chart_data": dual_chart_dump,
        "aspects": aspects_dump,
        "score": relationship_score["score_value"],
        "score_description": relationship_score["score_description"],
        "is_destiny_sign": relationship_score["is_destiny_sign"],
        "score_breakdown": relationship_score.get("score_breakdown", []),
    }
    model = rm.CompatibilityScoreResponseModel.model_validate(payload)
    assert isinstance(model.chart_data, DualChartDataModel)
    assert isinstance(model.aspects[0], RelationshipScoreAspectModel)
    assert model.score is not None
    assert model.score_description
    assert isinstance(model.score_breakdown, list)


def test_lunar_phase_events_response_model_parses_payload():
    payload = {
        "status": "OK",
        "from_iso": "2026-03-01T00:00:00+00:00",
        "horizon_days": 30,
        "events": [
            {
                "event": "new_moon",
                "at_utc": "2026-03-19T03:24:00+00:00",
                "target_angle_deg": 0.0,
                "angle_deg": 0.001,
            }
        ],
    }
    model = rm.LunarPhaseEventsResponseModel.model_validate(payload)
    assert model.status == "OK"
    assert model.horizon_days == 30
    assert len(model.events) == 1
    assert model.events[0].event == "new_moon"


def test_eclipse_events_response_model_parses_payload():
    payload = {
        "status": "OK",
        "from_iso": "2026-01-01T00:00:00+00:00",
        "horizon_days": 365,
        "event_types": ["solar", "lunar"],
        "solar_types": ["total", "annular", "partial", "annular_total"],
        "lunar_types": ["total", "partial", "penumbral"],
        "events": [
            {
                "event": "solar_eclipse",
                "eclipse_type": "annular",
                "at_utc": "2026-02-17T12:11:53.987477+00:00",
                "eclipse_begin_utc": "2026-02-17T09:56:47.676076+00:00",
                "eclipse_end_utc": "2026-02-17T14:27:40.254853+00:00",
                "magnitude": 0.9637550694,
                "saros_series": 121,
                "saros_member": 61,
                "is_central": True,
                "is_noncentral": False,
            }
        ],
    }
    model = rm.EclipseEventsResponseModel.model_validate(payload)
    assert model.status == "OK"
    assert model.horizon_days == 365
    assert model.event_types == ["solar", "lunar"]
    assert len(model.events) == 1
    assert model.events[0].event == "solar_eclipse"
    assert model.events[0].eclipse_type == "annular"


def test_ingress_events_response_model_parses_payload():
    payload = {
        "status": "OK",
        "from_iso": "2026-03-01T00:00:00+00:00",
        "horizon_days": 30,
        "planets": ["Sun", "Moon"],
        "events": [
            {
                "event": "sign_ingress",
                "planet": "Moon",
                "at_utc": "2026-03-01T12:00:00+00:00",
                "from_sign": "Can",
                "to_sign": "Leo",
            }
        ],
    }
    model = rm.IngressEventsResponseModel.model_validate(payload)
    assert model.status == "OK"
    assert model.horizon_days == 30
    assert model.planets == ["Sun", "Moon"]
    assert len(model.events) == 1
    assert model.events[0].event == "sign_ingress"


def test_aspect_events_response_model_parses_payload():
    payload = {
        "status": "OK",
        "from_iso": "2026-03-01T00:00:00+00:00",
        "horizon_days": 30,
        "planets": ["Sun", "Moon"],
        "pair_types": ["rapid_rapid"],
        "aspect_types": ["square", "opposition"],
        "events": [
            {
                "event": "planetary_aspect",
                "aspect": "square",
                "planet_1": "Sun",
                "planet_2": "Moon",
                "pair_type": "rapid_rapid",
                "target_angle_deg": 90.0,
                "at_utc": "2026-03-04T00:00:00+00:00",
                "orbit_deg": 0.001,
                "p1_speed": 0.985,
                "p2_speed": 13.217,
            }
        ],
    }
    model = rm.AspectEventsResponseModel.model_validate(payload)
    assert model.status == "OK"
    assert model.horizon_days == 30
    assert model.planets == ["Sun", "Moon"]
    assert model.pair_types == ["rapid_rapid"]
    assert model.aspect_types == ["square", "opposition"]
    assert len(model.events) == 1
    assert model.events[0].event == "planetary_aspect"
    assert model.events[0].aspect == "square"
