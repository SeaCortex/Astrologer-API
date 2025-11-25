from datetime import datetime, timezone
from logging import getLogger
from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse
from kerykeion import AstrologicalSubjectFactory, ChartDataFactory
from ..types.request_models import (
    NowChartRequestModel,
    NowSubjectRequestModel,
    BirthDataRequestModel,
    BirthChartDataRequestModel,
    BirthChartRequestModel,
)
from ..types.response_models import (
    SubjectResponseModel,
    ChartResponseModel,
    ChartDataResponseModel,
)
from ..utils.get_time_from_google import get_time_from_google
from ..utils.router_utils import (
    build_subject,
    chart_data_payload,
    chart_payload,
    create_natal_chart_data,
    dump,
    handle_exception,
    resolve_active_points,
    resolve_active_aspects,
)

logger = getLogger(__name__)
router = APIRouter()

@router.post("/api/v5/now/subject", response_model=SubjectResponseModel)
async def now_subject(request_body: NowSubjectRequestModel, request: Request) -> JSONResponse:
    """
    **POST** `/api/v5/now/subject`

    Returns an astrological subject computed for the current UTC time at Greenwich (offline mode).

    **Parameters:**
    - `name`, `zodiac_type`, `sidereal_mode`, `perspective_type`, `houses_system_identifier`

    **Returns:**
    - `status`: "OK"
    - `subject`: AstrologicalSubjectModel (serialized)
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

        return JSONResponse(
            content={
                "status": "OK",
                "subject": dump(subject),
            },
            status_code=200,
        )

    except Exception as exc:  # pragma: no cover - defensive
        return await handle_exception(exc, request)


@router.post("/api/v5/now/chart", response_model=ChartResponseModel)
async def now_chart(request_body: NowChartRequestModel, request: Request) -> JSONResponse:
    """
    **POST** `/api/v5/now/chart`

    Returns chart data and an SVG chart for the current UTC moment at Greenwich.

    **Parameters:**
    - `theme`, `language`
    - `split_chart` (if true returns chart_wheel and chart_grid, otherwise a single chart)
    - `transparent_background`
    - `show_house_position_comparison` (hide the comparison table when false)
    - `custom_title` (temporary title override, max 40 chars)
    - `active_points` / `active_aspects` (optional overrides)
    - `distribution_method`, `custom_distribution_weights` (optional)

    **Returns:**
    - `status`: "OK"
    - `chart_data`: ChartDataModel
    - `chart`: SVG string (when split_chart=false)
    - `chart_wheel`, `chart_grid`: SVGs (when split_chart=true)
    """
    logger.info(f"{request.url}: Current chart request")
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
            subject,
            active_points=resolve_active_points(request_body.active_points),
            active_aspects=resolve_active_aspects(request_body.active_aspects),
            distribution_method=request_body.distribution_method,
            custom_distribution_weights=request_body.custom_distribution_weights,
        )
        payload = chart_payload(
            chart_data,
            theme=request_body.theme,
            language=request_body.language,
            split_chart=request_body.split_chart,
            transparent_background=request_body.transparent_background,
            show_house_position_comparison=request_body.show_house_position_comparison,
            custom_title=request_body.custom_title,
        )
        return JSONResponse(content=payload, status_code=200)

    except Exception as exc:  # pragma: no cover - defensive
        return await handle_exception(exc, request)


@router.post("/api/v5/subject", response_model=SubjectResponseModel)
async def subject_data(birth_data_request: BirthDataRequestModel, request: Request) -> JSONResponse:
    """
    **POST** `/api/v5/subject`

    Builds and returns an astrological subject without rendering any chart.

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


@router.post("/api/v5/chart-data/natal", response_model=ChartDataResponseModel)
async def natal_chart_data(request_body: BirthChartDataRequestModel, request: Request) -> JSONResponse:
    """
    **POST** `/api/v5/chart-data/natal`

    Returns full natal chart data without SVG rendering.

    **Parameters:**
    - `subject`: SubjectModel
    - `active_points` / `active_aspects` (optional overrides)
    - `distribution_method`, `custom_distribution_weights` (optional)

    **Returns:**
    - `status`: "OK"
    - `chart_data`: ChartDataModel
    """
    logger.info(f"{request.url}: Natal chart data request")
    logger.debug(f"Request: {request.method} {request.url} Body: {request_body.model_dump_json()}")

    try:
        chart_data = create_natal_chart_data(request_body)
        return JSONResponse(content=chart_data_payload(chart_data), status_code=200)
    except Exception as exc:  # pragma: no cover - defensive
        return await handle_exception(exc, request)


@router.post("/api/v5/chart/natal", response_model=ChartResponseModel)
async def natal_chart(request_body: BirthChartRequestModel, request: Request) -> JSONResponse:
    """
    **POST** `/api/v5/chart/natal`

    Returns natal chart data and rendered SVG chart.

    **Parameters:**
    - `theme`, `language`
    - `split_chart` (if true returns chart_wheel and chart_grid, otherwise a single chart)
    - `transparent_background`
    - `show_house_position_comparison` (hide the comparison table when false)
    - `custom_title` (temporary title override, max 40 chars)

    **Returns:**
    - `status`: "OK"
    - `chart_data`: ChartDataModel
    - `chart`: SVG (when split_chart=false)
    - `chart_wheel`, `chart_grid`: SVGs (when split_chart=true)
    """
    logger.info(f"{request.url}: Natal chart request")
    logger.debug(f"Request: {request.method} {request.url} Body: {request_body.model_dump_json()}")

    try:
        chart_data = create_natal_chart_data(request_body)
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
