"""
Chart data endpoints - JSON data only.

All endpoints that return chart data without SVG rendering via /api/v5/chart-data/*.
"""

from logging import getLogger
from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse

from ..types.request_models import (
    BirthChartDataRequestModel,
    SynastryChartDataRequestModel,
    CompositeChartDataRequestModel,
    TransitChartDataRequestModel,
    PlanetaryReturnDataRequestModel,
)
from ..types.response_models import (
    ChartDataResponseModel,
)
from ..utils.router_utils import (
    calculate_return_chart_data,
    chart_data_payload,
    create_natal_chart_data,
    create_synastry_chart_data,
    create_composite_chart_data,
    create_transit_chart_data,
    handle_exception,
)

logger = getLogger(__name__)
router = APIRouter()


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
    logger.info(f"{request.url}: Natal chart data request")
    logger.debug(f"Request: {request.method} {request.url} Body: {request_body.model_dump_json()}")

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
    logger.info(f"{request.url}: Synastry chart data request")
    logger.debug(f"Request: {request.method} {request.url} Body: {request_body.model_dump_json()}")

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
    logger.info(f"{request.url}: Composite chart data request")
    logger.debug(f"Request: {request.method} {request.url} Body: {request_body.model_dump_json()}")

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
    logger.info(f"{request.url}: Transit chart data request")
    logger.debug(f"Request: {request.method} {request.url} Body: {request_body.model_dump_json()}")

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
    logger.info(f"{request.url}: Solar return data request")
    logger.debug(f"Request: {request.method} {request.url} Body: {request_body.model_dump_json()}")

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
    logger.info(f"{request.url}: Lunar return data request")
    logger.debug(f"Request: {request.method} {request.url} Body: {request_body.model_dump_json()}")

    try:
        chart_data = calculate_return_chart_data(request_body, "Lunar")
        return JSONResponse(content=chart_data_payload(chart_data), status_code=200)
    except Exception as exc:  # pragma: no cover - defensive
        return await handle_exception(exc, request)
