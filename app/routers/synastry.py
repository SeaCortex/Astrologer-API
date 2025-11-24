from logging import getLogger
from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse
from kerykeion import ChartDataFactory
from ..types.request_models import (
    SynastryChartDataRequestModel,
    SynastryChartRequestModel,
    RelationshipScoreRequestModel,
)
from ..types.response_models import (
    ChartDataResponseModel,
    ChartResponseModel,
    CompatibilityScoreResponseModel,
)
from ..utils.router_utils import (
    build_subject,
    chart_data_payload,
    chart_payload,
    create_synastry_chart_data,
    dump,
    handle_exception,
    resolve_active_points,
    resolve_active_aspects,
)

logger = getLogger(__name__)
router = APIRouter()

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


@router.post("/api/v5/charts/synastry", response_model=ChartResponseModel)
async def synastry_chart(request_body: SynastryChartRequestModel, request: Request) -> JSONResponse:
    """
    **POST** `/api/v5/charts/synastry`

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


@router.post("/api/v5/compatibility-score", response_model=CompatibilityScoreResponseModel)
async def compatibility_score(request_body: RelationshipScoreRequestModel, request: Request) -> JSONResponse:
    """
    **POST** `/api/v5/compatibility-score`

    Calculates the Ciro Discepolo compatibility score between two subjects.

    **Parameters:**
    - `first_subject`, `second_subject`
    - `active_points` / `active_aspects` overrides (optional)

    **Returns:**
    - `status`: "OK"
    - `score`, `score_description`, `is_destiny_sign`, `aspects`
    - `chart_data`: underlying Synastry chart data used for the calculation
    """
    logger.info(f"{request.url}: Compatibility score request")
    logger.debug(f"Request: {request.method} {request.url} Body: {request_body.model_dump_json()}")

    try:
        chart_data = ChartDataFactory.create_synastry_chart_data(
            build_subject(request_body.first_subject),
            build_subject(request_body.second_subject),
            active_points=resolve_active_points(request_body.active_points),
            active_aspects=resolve_active_aspects(request_body.active_aspects),
            include_relationship_score=True,
            include_house_comparison=True,
        )

        score_model = getattr(chart_data, "relationship_score", None)

        return JSONResponse(
            content={
                "status": "OK",
                "score": score_model.score_value if score_model else None,
                "score_description": score_model.score_description if score_model else None,
                "is_destiny_sign": score_model.is_destiny_sign if score_model else None,
                "aspects": dump(score_model.aspects) if score_model else [],
                "chart_data": dump(chart_data),
            },
            status_code=200,
        )

    except Exception as exc:  # pragma: no cover - defensive
        return await handle_exception(exc, request)
