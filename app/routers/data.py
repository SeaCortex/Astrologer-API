"""
Chart data endpoints - JSON data only.

All endpoints that return chart data without SVG rendering via /api/v5/chart-data/*.
"""

from datetime import datetime, timezone
from logging import getLogger
from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse

from ..types.request_models import (
    BirthDataRequestModel,
    BirthChartDataRequestModel,
    ConjunctionEventsRequestModel,
    EclipseEventsRequestModel,
    IngressEventsRequestModel,
    LunarPhaseEventsRequestModel,
    NowSubjectRequestModel,
    ProgressedMoonCycleRequestModel,
    RetrogradesNextRequestModel,
    SynastryChartDataRequestModel,
    CompositeChartDataRequestModel,
    TransitChartDataRequestModel,
    PlanetaryReturnDataRequestModel,
)
from ..types.response_models import (
    ChartDataResponseModel,
    ConjunctionEventsResponseModel,
    DerivedNatalProfileResponseModel,
    EclipseEventsResponseModel,
    IngressEventsResponseModel,
    LunarPhaseEventsResponseModel,
    ProgressedMoonCycleResponseModel,
    RetrogradesNextResponseModel,
    ReturnDataResponseModel,
    SubjectResponseModel,
    CompatibilityScoreResponseModel,
)
from ..utils.get_time_from_google import get_time_from_google
from ..utils.derived_profile import build_derived_natal_profile, ensure_required_derived_points
from ..utils.progressions import compute_progressed_moon_cycle, ensure_progressed_points
from ..utils.ingress import compute_ingress_events
from ..utils.lunar_events import compute_lunar_phase_events
from ..utils.retrogrades import compute_next_retrogrades, parse_iso_utc
from ..utils.conjunctions import compute_conjunction_events
from ..utils.eclipses import compute_eclipse_events
from ..utils.router_utils import (
    build_subject,
    calculate_return_chart_data,
    chart_data_payload,
    create_natal_chart_data,
    create_synastry_chart_data,
    create_composite_chart_data,
    create_transit_chart_data,
    dump,
    handle_exception,
    resolve_active_points,
)
from ..utils.logging_utils import log_request_with_body
from kerykeion import AstrologicalSubjectFactory

logger = getLogger(__name__)
router = APIRouter()


@router.post("/api/v5/subject", response_model=SubjectResponseModel)
async def subject_data(birth_data_request: BirthDataRequestModel, request: Request) -> JSONResponse:
    """
    **POST** `/api/v5/subject`

    Builds and returns an astrological subject.

    **Parameters:**
    - `subject`: SubjectModel (offline preferred or GeoNames via geonames_username)

    **Returns:**
    - `status`: "OK"
    - `subject`: AstrologicalSubjectModel (serialized)
    """
    log_request_with_body(logger, request, "Subject data request", birth_data_request.model_dump_json())

    try:
        active_points = resolve_active_points(birth_data_request.active_points)
        subject = build_subject(birth_data_request.subject, active_points=active_points)
        return JSONResponse(content={"status": "OK", "subject": dump(subject)}, status_code=200)

    except Exception as exc:  # pragma: no cover - defensive
        return await handle_exception(exc, request)


@router.post("/api/v5/now/subject", response_model=SubjectResponseModel)
async def now_subject(request_body: NowSubjectRequestModel, request: Request) -> JSONResponse:
    """
    **POST** `/api/v5/now/subject`

    Returns an astrological subject for the current UTC time at Greenwich.

    **Parameters:**
    - `name`, `zodiac_type`, `sidereal_mode`, `perspective_type`, `houses_system_identifier`

    **Returns:**
    - `status`: "OK"
    - `subject`: AstrologicalSubjectModel
    """
    log_request_with_body(logger, request, "Current subject request", request_body.model_dump_json())

    try:
        try:
            utc_datetime = get_time_from_google()
        except Exception as time_exc:  # pragma: no cover - fallback path
            logger.warning("Falling back to system UTC time: %s", time_exc)
            utc_datetime = datetime.now(timezone.utc)

        subject = AstrologicalSubjectFactory.from_birth_data(
            name=request_body.name,
            year=utc_datetime.year,  # type: ignore[arg-type]
            month=utc_datetime.month,  # type: ignore[arg-type]
            day=utc_datetime.day,  # type: ignore[arg-type]
            hour=utc_datetime.hour,  # type: ignore[arg-type]
            minute=utc_datetime.minute,  # type: ignore[arg-type]
            seconds=utc_datetime.second,  # type: ignore[arg-type]
            city="Greenwich",
            nation="GB",
            lng=-0.001545,
            lat=51.477928,
            tz_str="Etc/UTC",
            online=False,
            zodiac_type=request_body.zodiac_type,
            sidereal_mode=request_body.sidereal_mode,
            perspective_type=request_body.perspective_type,
            houses_system_identifier=request_body.houses_system_identifier,
            active_points=resolve_active_points(None),
            suppress_geonames_warning=True,
        )

        return JSONResponse(content={"status": "OK", "subject": dump(subject)}, status_code=200)

    except Exception as exc:  # pragma: no cover - defensive
        return await handle_exception(exc, request)


@router.post("/api/v5/derived/natal-profile", response_model=DerivedNatalProfileResponseModel)
async def derived_natal_profile(request_body: BirthDataRequestModel, request: Request) -> JSONResponse:
    """
    **POST** `/api/v5/derived/natal-profile`

    Returns derived Western-astrology natal metrics with normalized subject data.

    **Parameters:**
    - `subject`: SubjectModel
    - `active_points` (optional): Used to filter stellium/hemisphere point counting

    **Returns:**
    - `status`: "OK"
    - `subject`: AstrologicalSubjectModel
    - `derived_profile`: chart_ruler, stelliums, hemispheres, lunar_mansion
    """
    log_request_with_body(logger, request, "Derived natal profile request", request_body.model_dump_json())

    try:
        requested_active_points = resolve_active_points(request_body.active_points)
        active_points_for_subject = ensure_required_derived_points(requested_active_points)
        subject = build_subject(request_body.subject, active_points=active_points_for_subject)
        derived_profile = build_derived_natal_profile(subject, active_points=requested_active_points)

        return JSONResponse(
            content={
                "status": "OK",
                "subject": dump(subject),
                "derived_profile": dump(derived_profile),
            },
            status_code=200,
        )

    except Exception as exc:  # pragma: no cover - defensive
        return await handle_exception(exc, request)


@router.post("/api/v5/compatibility-score", response_model=CompatibilityScoreResponseModel)
async def compatibility_score(request_body: SynastryChartDataRequestModel, request: Request) -> JSONResponse:
    """
    **POST** `/api/v5/compatibility-score`

    Calculates Ciro Discepolo compatibility score between two subjects.

    **Parameters:**
    - `first_subject`, `second_subject`: SubjectModel
    - `active_points` / `active_aspects` overrides

    **Returns:**
    - `status`: "OK"
    - `score`: Compatibility score value
    - `score_description`: Text description of score
    - `is_destiny_sign`: Boolean indicating destiny sign relationship
    - `aspects`: List of aspects used in score calculation
    - `chart_data`: Full synastry chart data
    """
    log_request_with_body(logger, request, "Compatibility score request", request_body.model_dump_json())

    try:
        chart_data = create_synastry_chart_data(request_body)

        if not chart_data.relationship_score:  # pragma: no cover - defensive
            raise ValueError("Relationship score computation failed")

        return JSONResponse(
            content={
                "status": "OK",
                "score": chart_data.relationship_score.score_value,
                "score_description": chart_data.relationship_score.score_description,
                "is_destiny_sign": chart_data.relationship_score.is_destiny_sign,
                "aspects": dump(chart_data.relationship_score.aspects),
                "score_breakdown": dump(chart_data.relationship_score.score_breakdown),
                "chart_data": dump(chart_data),
            },
            status_code=200,
        )

    except Exception as exc:  # pragma: no cover - defensive
        return await handle_exception(exc, request)


@router.post("/api/v5/chart-data/birth-chart", response_model=ChartDataResponseModel)
async def natal_chart_data(request_body: BirthChartDataRequestModel, request: Request) -> JSONResponse:
    """
    **POST** `/api/v5/chart-data/birth-chart`

    Returns full natal chart data without SVG rendering.

    **Parameters:**
    - `subject`: SubjectModel
    - `active_points` / `active_aspects` (optional overrides)
    - `distribution_method`, `custom_distribution_weights` (optional)

    **Returns:**
    - `status`: "OK"
    - `chart_data`: ChartDataModel
    """
    log_request_with_body(logger, request, "Natal chart data request", request_body.model_dump_json())

    try:
        chart_data = create_natal_chart_data(request_body)
        return JSONResponse(content=chart_data_payload(chart_data), status_code=200)
    except Exception as exc:  # pragma: no cover - defensive
        return await handle_exception(exc, request)


@router.post("/api/v5/chart-data/synastry", response_model=ChartDataResponseModel)
async def synastry_chart_data(request_body: SynastryChartDataRequestModel, request: Request) -> JSONResponse:
    """
    **POST** `/api/v5/chart-data/synastry`

    Returns synastry chart data comparing two subjects; no SVG rendering.

    **Parameters:**
    - `first_subject`, `second_subject`: SubjectModel
    - `include_house_comparison`, `include_relationship_score` (flags)
    - `active_points` / `active_aspects` overrides

    **Returns:**
    - `status`: "OK"
    - `chart_data`: ChartDataModel
    """
    log_request_with_body(logger, request, "Synastry chart data request", request_body.model_dump_json())

    try:
        chart_data = create_synastry_chart_data(request_body)
        return JSONResponse(content=chart_data_payload(chart_data), status_code=200)
    except Exception as exc:  # pragma: no cover - defensive
        return await handle_exception(exc, request)


@router.post("/api/v5/chart-data/composite", response_model=ChartDataResponseModel)
async def composite_chart_data(request_body: CompositeChartDataRequestModel, request: Request) -> JSONResponse:
    """
    **POST** `/api/v5/chart-data/composite`

    Returns midpoint composite chart data (no SVG rendering).

    **Parameters:**
    - `first_subject`, `second_subject`
    - `active_points` / `active_aspects` overrides

    **Returns:**
    - `status`: "OK"
    - `chart_data`: ChartDataModel
    """
    log_request_with_body(logger, request, "Composite chart data request", request_body.model_dump_json())

    try:
        chart_data = create_composite_chart_data(request_body)
        return JSONResponse(content=chart_data_payload(chart_data), status_code=200)
    except Exception as exc:  # pragma: no cover - defensive
        return await handle_exception(exc, request)


@router.post("/api/v5/chart-data/transit", response_model=ChartDataResponseModel)
async def transit_chart_data(request_body: TransitChartDataRequestModel, request: Request) -> JSONResponse:
    """
    **POST** `/api/v5/chart-data/transit`

    Returns transit analysis data (current/selected transits to natal chart), no SVG.

    **Parameters:**
    - `first_subject`: SubjectModel (natal)
    - `transit_subject`: SubjectModel (transit moment)
    - `include_house_comparison` flag

    **Returns:**
    - `status`: "OK"
    - `chart_data`: ChartDataModel
    """
    log_request_with_body(logger, request, "Transit chart data request", request_body.model_dump_json())

    try:
        chart_data = create_transit_chart_data(request_body)
        return JSONResponse(content=chart_data_payload(chart_data), status_code=200)
    except Exception as exc:  # pragma: no cover - defensive
        return await handle_exception(exc, request)


@router.post("/api/v5/chart-data/solar-return", response_model=ChartDataResponseModel)
async def solar_return_data(request_body: PlanetaryReturnDataRequestModel, request: Request) -> JSONResponse:
    """
    **POST** `/api/v5/chart-data/solar-return`

    Calculates the solar return for a given year/month/instant and returns data only.

    **Parameters:**
    - `subject`: SubjectModel (natal)
    - `year` or `month`+`year` or `iso_datetime`
    - `wheel_type`: "dual"|"single" (affects data model)

    **Returns:**
    - `status`: "OK"
    - `chart_data`: ChartDataModel
    """
    log_request_with_body(logger, request, "Solar return data request", request_body.model_dump_json())

    try:
        chart_data = calculate_return_chart_data(request_body, "Solar")
        return JSONResponse(content=chart_data_payload(chart_data), status_code=200)
    except Exception as exc:  # pragma: no cover - defensive
        return await handle_exception(exc, request)


@router.post("/api/v5/chart-data/lunar-return", response_model=ChartDataResponseModel)
async def lunar_return_data(request_body: PlanetaryReturnDataRequestModel, request: Request) -> JSONResponse:
    """
    **POST** `/api/v5/chart-data/lunar-return`

    Calculates the lunar return and returns data only.

    **Parameters:**
    - Same as solar-return chart-data.

    **Returns:**
    - `status`: "OK"
    - `chart_data`: ChartDataModel
    """
    log_request_with_body(logger, request, "Lunar return data request", request_body.model_dump_json())

    try:
        chart_data = calculate_return_chart_data(request_body, "Lunar")
        return JSONResponse(content=chart_data_payload(chart_data), status_code=200)
    except Exception as exc:  # pragma: no cover - defensive
        return await handle_exception(exc, request)


@router.post("/api/v5/chart-data/saturn-return", response_model=ReturnDataResponseModel)
async def saturn_return_data(request_body: PlanetaryReturnDataRequestModel, request: Request) -> JSONResponse:
    """
    **POST** `/api/v5/chart-data/saturn-return`

    Calculates Saturn return chart data.
    """
    log_request_with_body(logger, request, "Saturn return data request", request_body.model_dump_json())

    try:
        chart_data = calculate_return_chart_data(request_body, "Saturn")
        return JSONResponse(
            content={
                "status": "OK",
                "chart_data": dump(chart_data),
                "return_type": "Saturn",
                "wheel_type": request_body.wheel_type,
            },
            status_code=200,
        )
    except Exception as exc:  # pragma: no cover - defensive
        return await handle_exception(exc, request)


@router.post("/api/v5/chart-data/jupiter-return", response_model=ReturnDataResponseModel)
async def jupiter_return_data(request_body: PlanetaryReturnDataRequestModel, request: Request) -> JSONResponse:
    """
    **POST** `/api/v5/chart-data/jupiter-return`

    Calculates Jupiter return chart data.
    """
    log_request_with_body(logger, request, "Jupiter return data request", request_body.model_dump_json())

    try:
        chart_data = calculate_return_chart_data(request_body, "Jupiter")
        return JSONResponse(
            content={
                "status": "OK",
                "chart_data": dump(chart_data),
                "return_type": "Jupiter",
                "wheel_type": request_body.wheel_type,
            },
            status_code=200,
        )
    except Exception as exc:  # pragma: no cover - defensive
        return await handle_exception(exc, request)


@router.post("/api/v5/chart-data/lunar-node-return", response_model=ReturnDataResponseModel)
async def lunar_node_return_data(request_body: PlanetaryReturnDataRequestModel, request: Request) -> JSONResponse:
    """
    **POST** `/api/v5/chart-data/lunar-node-return`

    Calculates mean north lunar node return chart data.
    """
    log_request_with_body(logger, request, "Lunar node return data request", request_body.model_dump_json())

    try:
        chart_data = calculate_return_chart_data(request_body, "MeanNode")
        return JSONResponse(
            content={
                "status": "OK",
                "chart_data": dump(chart_data),
                "return_type": "MeanNode",
                "wheel_type": request_body.wheel_type,
            },
            status_code=200,
        )
    except Exception as exc:  # pragma: no cover - defensive
        return await handle_exception(exc, request)


@router.post("/api/v5/chart-data/progressed-moon-cycle", response_model=ProgressedMoonCycleResponseModel)
async def progressed_moon_cycle(request_body: ProgressedMoonCycleRequestModel, request: Request) -> JSONResponse:
    """
    **POST** `/api/v5/chart-data/progressed-moon-cycle`

    Computes secondary progressed Moon cycle data, including progressed lunation phase
    and next Moon sign/house ingress events on the target timeline.
    """
    log_request_with_body(logger, request, "Progressed moon cycle request", request_body.model_dump_json())

    try:
        requested_active_points = resolve_active_points(request_body.active_points)
        active_points_for_progressions = ensure_progressed_points(requested_active_points)
        natal_subject = build_subject(request_body.subject, active_points=active_points_for_progressions)

        progression_data = compute_progressed_moon_cycle(
            natal_subject=natal_subject,
            target_iso_datetime=request_body.target_iso_datetime,
            range_end_iso_datetime=request_body.range_end_iso_datetime,
            step_days=request_body.step_days,
            active_points=active_points_for_progressions,
        )
        return JSONResponse(content={"status": "OK", "progressed_moon_cycle": dump(progression_data)}, status_code=200)
    except Exception as exc:  # pragma: no cover - defensive
        return await handle_exception(exc, request)


@router.post("/api/v5/events/retrogrades", response_model=RetrogradesNextResponseModel)
async def retrogrades_next(request_body: RetrogradesNextRequestModel, request: Request) -> JSONResponse:
    """
    **POST** `/api/v5/events/retrogrades`

    Computes next retrograde windows for selected planets using streaming scan logic.

    **Semantics (`include_ongoing`):**
    - If `include_ongoing=true` and a planet is already retrograde at `from_iso`,
      the current window is returned with:
      - `is_ongoing=true`
      - `started_before_from=true`
    - If `include_ongoing=false`, only strictly future windows are returned
      (`next_start_utc > from_iso`).

    **Parameters:**
    - `from_iso` (optional): UTC ISO start time. Defaults to current UTC.
    - `horizon_days` (required): Lookahead horizon in days (max 2 years).
    - `planets` (required): Planet list from allowlist (case-insensitive, deduplicated).
    - `include_ongoing` (optional, default true): Include windows already in progress.

    **Returns:**
    - `status`: "OK"
    - `from_iso`: Effective UTC start used by the scanner.
    - `horizon_days`: Requested lookahead days.
    - `include_ongoing`: Echo of request flag.
    - `retrogrades`: One next retrograde window per requested planet.
    """
    log_request_with_body(logger, request, "Retrogrades next request", request_body.model_dump_json())

    try:
        from_utc = (
            datetime.now(timezone.utc)
            if request_body.from_iso is None
            else parse_iso_utc(request_body.from_iso)
        )

        retrogrades = compute_next_retrogrades(
            from_utc=from_utc,
            horizon_days=request_body.horizon_days,
            planets=request_body.planets,
            include_ongoing=request_body.include_ongoing,
        )

        return JSONResponse(
            content={
                "status": "OK",
                "from_iso": from_utc.isoformat(),
                "horizon_days": request_body.horizon_days,
                "include_ongoing": request_body.include_ongoing,
                "retrogrades": retrogrades,
            },
            status_code=200,
        )
    except Exception as exc:  # pragma: no cover - defensive
        return await handle_exception(exc, request)


@router.post("/api/v5/events/lunar-phases", response_model=LunarPhaseEventsResponseModel)
async def lunar_phase_events(request_body: LunarPhaseEventsRequestModel, request: Request) -> JSONResponse:
    """
    **POST** `/api/v5/events/lunar-phases`

    Detects exact lunar phase events in a lookahead window using scan + refine logic.

    **Parameters:**
    - `from_iso` (optional): UTC ISO start time. Defaults to current UTC.
    - `horizon_days` (required): Lookahead horizon in days (max 5 years).
    - `include_distance_metrics` (optional): Include Moon-Earth distance/perigee/apogee metrics.
    - `include_super_luna` (optional): Include Super Luna classification for New/Full Moon.
    - `super_luna_definition` (optional): `nolle_90pct_cycle` or `distance_threshold_km`.
    - `super_luna_distance_km_threshold` (optional): Threshold used for `distance_threshold_km`.

    **Returns:**
    - `status`: "OK"
    - `from_iso`: Effective UTC start used by the scanner.
    - `horizon_days`: Requested lookahead days.
    - `events`: Exact New Moon / First Quarter / Full Moon / Last Quarter timestamps.
    """
    log_request_with_body(logger, request, "Lunar phase events request", request_body.model_dump_json())

    try:
        from_utc = (
            datetime.now(timezone.utc)
            if request_body.from_iso is None
            else parse_iso_utc(request_body.from_iso)
        )
        computed = compute_lunar_phase_events(
            from_utc=from_utc,
            horizon_days=request_body.horizon_days,
            include_distance_metrics=request_body.include_distance_metrics,
            include_super_luna=request_body.include_super_luna,
            super_luna_definition=request_body.super_luna_definition,
            super_luna_distance_km_threshold=request_body.super_luna_distance_km_threshold,
        )
        response_payload = {
            "status": "OK",
            "from_iso": from_utc.isoformat(),
            "horizon_days": request_body.horizon_days,
            "events": computed["events"],
        }
        if "distance_frame" in computed:
            response_payload["distance_frame"] = computed["distance_frame"]
        if "distance_units" in computed:
            response_payload["distance_units"] = computed["distance_units"]
        if "super_luna_definition_applied" in computed:
            response_payload["super_luna_definition_applied"] = computed["super_luna_definition_applied"]
        if "super_luna_distance_km_threshold_applied" in computed:
            response_payload["super_luna_distance_km_threshold_applied"] = computed[
                "super_luna_distance_km_threshold_applied"
            ]

        return JSONResponse(content=response_payload, status_code=200)
    except Exception as exc:  # pragma: no cover - defensive
        return await handle_exception(exc, request)


@router.post("/api/v5/events/eclipses", response_model=EclipseEventsResponseModel)
async def eclipse_events(request_body: EclipseEventsRequestModel, request: Request) -> JSONResponse:
    """
    **POST** `/api/v5/events/eclipses`

    Detects exact solar and lunar eclipse events in a lookahead window.

    **Parameters:**
    - `from_iso` (optional): UTC ISO start time. Defaults to current UTC.
    - `horizon_days` (required): Lookahead horizon in days (max 10 years).
    - `event_types` (optional): Include `solar`, `lunar`, or both.
    - `solar_types` (optional): Solar eclipse subtype filters.
    - `lunar_types` (optional): Lunar eclipse subtype filters.

    **Returns:**
    - `status`: "OK"
    - `from_iso`: Effective UTC start used by the scanner.
    - `horizon_days`: Requested lookahead days.
    - `event_types`: Effective normalized eclipse families.
    - `solar_types`: Effective normalized solar subtype filters.
    - `lunar_types`: Effective normalized lunar subtype filters.
    - `events`: Exact eclipse timestamps and type-specific metadata.
    """
    log_request_with_body(logger, request, "Eclipse events request", request_body.model_dump_json())

    try:
        from_utc = (
            datetime.now(timezone.utc)
            if request_body.from_iso is None
            else parse_iso_utc(request_body.from_iso)
        )

        events = compute_eclipse_events(
            from_utc=from_utc,
            horizon_days=request_body.horizon_days,
            event_types=request_body.event_types,
            solar_types=request_body.solar_types,
            lunar_types=request_body.lunar_types,
        )
        return JSONResponse(
            content={
                "status": "OK",
                "from_iso": from_utc.isoformat(),
                "horizon_days": request_body.horizon_days,
                "event_types": request_body.event_types,
                "solar_types": request_body.solar_types,
                "lunar_types": request_body.lunar_types,
                "events": events,
            },
            status_code=200,
        )
    except Exception as exc:  # pragma: no cover - defensive
        return await handle_exception(exc, request)


@router.post("/api/v5/events/ingress", response_model=IngressEventsResponseModel)
async def ingress_events(request_body: IngressEventsRequestModel, request: Request) -> JSONResponse:
    """
    **POST** `/api/v5/events/ingress`

    Detects exact planetary zodiac sign ingress events in a lookahead window using scan + refine logic.

    **Parameters:**
    - `from_iso` (optional): UTC ISO start time. Defaults to current UTC.
    - `horizon_days` (required): Lookahead horizon in days (max 2 years).
    - `planets` (optional): Planets to scan. Defaults to Sun, Moon, and all major planets.
      Supports `Mean_Lilith` and `True_Lilith` when explicitly provided.

    **Returns:**
    - `status`: "OK"
    - `from_iso`: Effective UTC start used by the scanner.
    - `horizon_days`: Requested lookahead days.
    - `planets`: Effective normalized planet list.
    - `events`: Exact sign ingress timestamps.
    """
    log_request_with_body(logger, request, "Ingress events request", request_body.model_dump_json())

    try:
        from_utc = (
            datetime.now(timezone.utc)
            if request_body.from_iso is None
            else parse_iso_utc(request_body.from_iso)
        )

        events = compute_ingress_events(
            from_utc=from_utc,
            horizon_days=request_body.horizon_days,
            planets=request_body.planets,
        )
        return JSONResponse(
            content={
                "status": "OK",
                "from_iso": from_utc.isoformat(),
                "horizon_days": request_body.horizon_days,
                "planets": request_body.planets,
                "events": events,
            },
            status_code=200,
        )
    except Exception as exc:  # pragma: no cover - defensive
        return await handle_exception(exc, request)


@router.post("/api/v5/events/conjunctions", response_model=ConjunctionEventsResponseModel)
async def conjunction_events(request_body: ConjunctionEventsRequestModel, request: Request) -> JSONResponse:
    """
    **POST** `/api/v5/events/conjunctions`

    Detects exact major planetary conjunction events in a lookahead window using stream scan + refine logic.

    **Parameters:**
    - `from_iso` (optional): UTC ISO start time. Defaults to current UTC.
    - `horizon_days` (required): Lookahead horizon in days (max 10 years).
    - `planets` (optional): Planets to scan for pairwise conjunctions.
    - `pair_types` (optional): Pair classes to include (`rapid_slow`, `slow_slow`, `rapid_rapid`).

    **Returns:**
    - `status`: "OK"
    - `from_iso`: Effective UTC start used by the scanner.
    - `horizon_days`: Requested lookahead days.
    - `planets`: Effective normalized planet list.
    - `pair_types`: Effective normalized pair category list.
    - `events`: Exact conjunction timestamps.
    """
    log_request_with_body(logger, request, "Conjunction events request", request_body.model_dump_json())

    try:
        from_utc = (
            datetime.now(timezone.utc)
            if request_body.from_iso is None
            else parse_iso_utc(request_body.from_iso)
        )

        events = compute_conjunction_events(
            from_utc=from_utc,
            horizon_days=request_body.horizon_days,
            planets=request_body.planets,
            pair_types=request_body.pair_types,
        )
        return JSONResponse(
            content={
                "status": "OK",
                "from_iso": from_utc.isoformat(),
                "horizon_days": request_body.horizon_days,
                "planets": request_body.planets,
                "pair_types": request_body.pair_types,
                "events": events,
            },
            status_code=200,
        )
    except Exception as exc:  # pragma: no cover - defensive
        return await handle_exception(exc, request)
