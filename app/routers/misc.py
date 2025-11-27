"""
Miscellaneous endpoints.

Health check, subject endpoints, now endpoints, and compatibility score.
"""

from datetime import datetime, timezone
from logging import getLogger
from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse

from ..config.settings import settings
from ..types.request_models import (
    BirthDataRequestModel,
    NowSubjectRequestModel,
    NowChartRequestModel,
    SynastryChartDataRequestModel,
)
from ..types.response_models import (
    StatusResponseModel,
    ApiStatusResponseModel,
    SubjectResponseModel,
    ChartResponseModel,
    CompatibilityScoreResponseModel,
)
from ..utils.get_time_from_google import get_time_from_google
from ..utils.router_utils import (
    build_subject,
    chart_payload,
    create_synastry_chart_data,
    dump,
    handle_exception,
    resolve_active_points,
    resolve_active_aspects,
)
from kerykeion import AstrologicalSubjectFactory, ChartDataFactory

logger = getLogger(__name__)
router = APIRouter()


@router.get("/api/v5/health", response_description="Health check", include_in_schema=False, response_model=StatusResponseModel)
async def health(request: Request) -> JSONResponse:
    """
    **GET** `/api/v5/health`

    Simple liveness probe for the API.

    **Returns:**
    - `status`: "OK"
    """
    logger.info(f"{request.url}: Health check")
    logger.debug(f"Request: {request.method} {request.url}")
    return JSONResponse(content={"status": "OK"}, status_code=200)


@router.get("/", response_description="Status of the API", include_in_schema=False, response_model=ApiStatusResponseModel)
async def status(request: Request) -> JSONResponse:
    """
    **GET** `/`

    Returns basic API status and environment information. Not included in the public schema.

    **Returns:**
    - `status`: "OK"
    - `environment`: deployment environment name
    - `debug`: whether debug mode is enabled
    """
    logger.info(f"{request.url}: API is up and running")
    logger.debug(f"Request: {request.method} {request.url}")
    response_dict = {
        "status": "OK",
        "environment": settings.env_type,
        "debug": settings.debug,
    }
    return JSONResponse(content=response_dict, status_code=200)


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
    logger.info(f"{request.url}: Subject data request")
    logger.debug(f"Request: {request.method} {request.url} Body: {birth_data_request.model_dump_json()}")

    try:
        subject = build_subject(birth_data_request.subject)
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
    logger.info(f"{request.url}: Current subject request")
    logger.debug(f"Request: {request.method} {request.url} Body: {request_body.model_dump_json()}")

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


@router.post("/api/v5/now/chart", response_model=ChartResponseModel)
async def now_chart(request_body: NowChartRequestModel, request: Request) -> JSONResponse:
    """
    **POST** `/api/v5/now/chart`

    Returns chart data and SVG for the current UTC time at Greenwich.

    **Parameters:**
    - `name`, configuration, rendering options

    **Returns:**
    - `status`: "OK"
    - `chart_data`: ChartDataModel
    - `chart`: SVG (or `chart_wheel` + `chart_grid`)
    """
    logger.info(f"{request.url}: Current time chart request")
    logger.debug(f"Request: {request.method} {request.url} Body: {request_body.model_dump_json()}")

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
            active_points=resolve_active_points(request_body.active_points),
            suppress_geonames_warning=True,
        )

        chart_data = ChartDataFactory.create_natal_chart_data(
            subject=subject,
            active_aspects=resolve_active_aspects(request_body.active_aspects),
            distribution_method=request_body.distribution_method,
            custom_distribution_weights=request_body.custom_distribution_weights,
        )

        payload = chart_payload(
            chart_data,
            request_body.theme,
            request_body.language,
            request_body.split_chart,
            request_body.transparent_background,
            request_body.show_house_position_comparison,
            request_body.custom_title,
        )
        return JSONResponse(content=payload, status_code=200)

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
    logger.info(f"{request.url}: Compatibility score request")
    logger.debug(f"Request: {request.method} {request.url} Body: {request_body.model_dump_json()}")

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
                "chart_data": dump(chart_data),
            },
            status_code=200,
        )

    except Exception as exc:  # pragma: no cover - defensive
        return await handle_exception(exc, request)
