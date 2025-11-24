from logging import getLogger
from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse
from ..types.request_models import (
    PlanetaryReturnDataRequestModel,
    PlanetaryReturnRequestModel,
)
from ..types.response_models import (
    ChartDataResponseModel,
    ReturnChartResponseModel,
)
from ..utils.router_utils import (
    calculate_return_chart_data,
    chart_data_payload,
    chart_payload,
    handle_exception,
)

logger = getLogger(__name__)
router = APIRouter()

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
        return handle_exception(exc, request)


@router.post("/api/v5/charts/solar-return", response_model=ReturnChartResponseModel)
async def solar_return_chart(request_body: PlanetaryReturnRequestModel, request: Request) -> JSONResponse:
    """
    **POST** `/api/v5/charts/solar-return`

    Returns solar return data and rendered SVG chart.

    **Parameters:**
    - `theme`, `language`, `split_chart`, `transparent_background`, `show_house_position_comparison`, `custom_title`

    **Returns:**
    - `return_type`: "Solar"
    - `wheel_type`: "dual" | "single"
    - `chart` (or `chart_wheel` + `chart_grid`)
    """
    logger.info(f"{request.url}: Solar return chart request")
    logger.debug(f"Request: {request.method} {request.url} Body: {request_body.model_dump_json()}")

    try:
        chart_data = calculate_return_chart_data(request_body, "Solar")
        payload = chart_payload(
            chart_data,
            request_body.theme,
            request_body.language,
            request_body.split_chart,
            request_body.transparent_background,
            request_body.show_house_position_comparison,
            request_body.custom_title,
        )
        payload["return_type"] = "Solar"
        payload["wheel_type"] = request_body.wheel_type
        return JSONResponse(content=payload, status_code=200)
    except Exception as exc:  # pragma: no cover - defensive
        return handle_exception(exc, request)


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
        return handle_exception(exc, request)


@router.post("/api/v5/charts/lunar-return", response_model=ReturnChartResponseModel)
async def lunar_return_chart(request_body: PlanetaryReturnRequestModel, request: Request) -> JSONResponse:
    """
    **POST** `/api/v5/charts/lunar-return`

    Returns lunar return data and rendered SVG chart.

    **Parameters:**
    - `theme`, `language`, `split_chart`, `transparent_background`, `show_house_position_comparison`, `custom_title`

    **Returns:**
    - `return_type`: "Lunar"
    - `wheel_type`: "dual" | "single"
    - `chart` (or `chart_wheel` + `chart_grid`)
    """
    logger.info(f"{request.url}: Lunar return chart request")
    logger.debug(f"Request: {request.method} {request.url} Body: {request_body.model_dump_json()}")

    try:
        chart_data = calculate_return_chart_data(request_body, "Lunar")
        payload = chart_payload(
            chart_data,
            request_body.theme,
            request_body.language,
            request_body.split_chart,
            request_body.transparent_background,
            request_body.show_house_position_comparison,
            request_body.custom_title,
        )
        payload["return_type"] = "Lunar"
        payload["wheel_type"] = request_body.wheel_type
        return JSONResponse(content=payload, status_code=200)
    except Exception as exc:  # pragma: no cover - defensive
        return handle_exception(exc, request)
