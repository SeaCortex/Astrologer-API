"""
Chart endpoints - SVG rendering.

All endpoints that return rendered SVG charts via /api/v5/chart/*.
"""

from logging import getLogger
from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse

from ..types.request_models import (
    BirthChartRequestModel,
    SynastryChartRequestModel,
    CompositeChartRequestModel,
    TransitChartRequestModel,
    PlanetaryReturnRequestModel,
)
from ..types.response_models import (
    ChartResponseModel,
    ReturnChartResponseModel,
)
from ..utils.router_utils import (
    calculate_return_chart_data,
    chart_payload,
    create_natal_chart_data,
    create_synastry_chart_data,
    create_composite_chart_data,
    create_transit_chart_data,
    handle_exception,
)

logger = getLogger(__name__)
router = APIRouter()


@router.post("/api/v5/chart/birth-chart", response_model=ChartResponseModel)
async def natal_chart(request_body: BirthChartRequestModel, request: Request) -> JSONResponse:
    """
    **POST** `/api/v5/chart/birth-chart`

    Returns birth chart data and rendered SVG chart.

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
    logger.info(f"{request.url}: Birth chart request")
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


@router.post("/api/v5/chart/synastry", response_model=ChartResponseModel)
async def synastry_chart(request_body: SynastryChartRequestModel, request: Request) -> JSONResponse:
    """
    **POST** `/api/v5/chart/synastry`

    Returns synastry chart data and a dual-wheel SVG chart.

    **Parameters:**
    - `theme`, `language`, `split_chart`, `transparent_background`
    - `show_house_position_comparison`, `custom_title`

    **Returns:**
    - `chart` (or `chart_wheel` + `chart_grid` when split_chart=true)
    - `chart_data`
    """
    logger.info(f"{request.url}: Synastry chart request")
    logger.debug(f"Request: {request.method} {request.url} Body: {request_body.model_dump_json()}")

    try:
        chart_data = create_synastry_chart_data(request_body)
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


@router.post("/api/v5/chart/composite", response_model=ChartResponseModel)
async def composite_chart(request_body: CompositeChartRequestModel, request: Request) -> JSONResponse:
    """
    **POST** `/api/v5/chart/composite`

    Returns composite chart data and rendered SVG chart.

    **Parameters:**
    - `theme`, `language`, `split_chart`, `transparent_background`, `show_house_position_comparison`, `custom_title`

    **Returns:**
    - `chart` (or `chart_wheel` + `chart_grid`)
    - `chart_data`
    """
    logger.info(f"{request.url}: Composite chart request")
    logger.debug(f"Request: {request.method} {request.url} Body: {request_body.model_dump_json()}")

    try:
        chart_data = create_composite_chart_data(request_body)
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


@router.post("/api/v5/chart/transit", response_model=ChartResponseModel)
async def transit_chart(request_body: TransitChartRequestModel, request: Request) -> JSONResponse:
    """
    **POST** `/api/v5/chart/transit`

    Returns transit data and rendered SVG chart.

    **Parameters:**
    - `theme`, `language`, `split_chart`, `transparent_background`, `show_house_position_comparison`, `custom_title`

    **Returns:**
    - `chart` (or `chart_wheel` + `chart_grid`)
    - `chart_data`
    """
    logger.info(f"{request.url}: Transit chart request")
    logger.debug(f"Request: {request.method} {request.url} Body: {request_body.model_dump_json()}")

    try:
        chart_data = create_transit_chart_data(request_body)
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


@router.post("/api/v5/chart/solar-return", response_model=ReturnChartResponseModel)
async def solar_return_chart(request_body: PlanetaryReturnRequestModel, request: Request) -> JSONResponse:
    """
    **POST** `/api/v5/chart/solar-return`

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
        return await handle_exception(exc, request)


@router.post("/api/v5/chart/lunar-return", response_model=ReturnChartResponseModel)
async def lunar_return_chart(request_body: PlanetaryReturnRequestModel, request: Request) -> JSONResponse:
    """
    **POST** `/api/v5/chart/lunar-return`

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
        return await handle_exception(exc, request)
