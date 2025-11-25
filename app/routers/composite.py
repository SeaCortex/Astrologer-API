from logging import getLogger
from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse
from ..types.request_models import (
    CompositeChartDataRequestModel,
    CompositeChartRequestModel,
)
from ..types.response_models import (
    ChartDataResponseModel,
    ChartResponseModel,
)
from ..utils.router_utils import (
    chart_data_payload,
    chart_payload,
    create_composite_chart_data,
    handle_exception,
)

logger = getLogger(__name__)
router = APIRouter()

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
