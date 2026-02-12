from typing import Literal, Optional, Union

from pydantic import BaseModel, Field

from kerykeion.schemas.kr_models import (
    AstrologicalSubjectModel,
    DualChartDataModel,
    KerykeionPointModel,
    RelationshipScoreAspectModel,
    SingleChartDataModel,
    ScoreBreakdownItemModel,
)


class StatusResponseModel(BaseModel):
    """Response payload containing only the status field."""

    status: str = Field(description="The status of the response.")


class ApiStatusResponseModel(StatusResponseModel):
    """Response payload for the API root status endpoint."""

    environment: str = Field(description="Deployment environment identifier.")
    debug: bool = Field(description="Whether debug mode is enabled.")


class SubjectResponseModel(StatusResponseModel):
    """Response payload containing a single astrological subject."""

    subject: AstrologicalSubjectModel = Field(description="Computed astrological subject.")


class ChartDataResponseModel(StatusResponseModel):
    """Response payload returning serialized chart data."""

    chart_data: Union[SingleChartDataModel, DualChartDataModel] = Field(description="Serialized chart data payload.")


class ChartResponseModel(ChartDataResponseModel):
    """Response payload returning chart data with optional rendered SVG assets."""

    chart: Optional[str] = Field(
        default=None,
        description="SVG representation of the chart when split charts are disabled.",
    )
    chart_wheel: Optional[str] = Field(
        default=None,
        description="SVG representation of the chart wheel when split charts are enabled.",
    )
    chart_grid: Optional[str] = Field(
        default=None,
        description="SVG representation of the aspect grid when split charts are enabled.",
    )


class ReturnChartResponseModel(ChartResponseModel):
    """Response payload for solar and lunar return chart requests."""

    return_type: Literal["Solar", "Lunar"] = Field(description="Type of planetary return.")
    wheel_type: Literal["dual", "single"] = Field(description="Rendered wheel configuration.")


class ReturnDataResponseModel(ChartDataResponseModel):
    """Response payload for JSON-only return data endpoints."""

    return_type: Literal["Solar", "Lunar", "Saturn", "Jupiter", "MeanNode"] = Field(
        description="Type of planetary return."
    )
    wheel_type: Literal["dual", "single"] = Field(description="Requested wheel configuration.")


class ChartRulerModel(BaseModel):
    """Derived chart ruler payload."""

    asc_sign: str = Field(description="Ascendant sign abbreviation.")
    ruler_point_name: str = Field(description="Name of the chart ruler point.")
    ruler_point: Optional[KerykeionPointModel] = Field(
        default=None,
        description="Computed chart ruler point details when available.",
    )


class SignStelliumModel(BaseModel):
    """Stellium grouping by sign."""

    sign: str = Field(description="Zodiac sign abbreviation.")
    points: list[str] = Field(description="Point names in the sign.")


class HouseStelliumModel(BaseModel):
    """Stellium grouping by house."""

    house: str = Field(description="House identifier.")
    points: list[str] = Field(description="Point names in the house.")


class StelliumsModel(BaseModel):
    """Stellium analysis payload."""

    min_count: int = Field(description="Minimum point count used to classify stelliums.")
    by_sign: list[SignStelliumModel] = Field(default_factory=list, description="Stelliums by zodiac sign.")
    by_house: list[HouseStelliumModel] = Field(default_factory=list, description="Stelliums by house.")


class HemisphereBreakdownModel(BaseModel):
    """Counts and percentages for a hemispheric axis."""

    above_count: Optional[int] = Field(default=None, description="Points above horizon (houses 7-12).")
    below_count: Optional[int] = Field(default=None, description="Points below horizon (houses 1-6).")
    above_pct: Optional[float] = Field(default=None, description="Percentage above horizon.")
    below_pct: Optional[float] = Field(default=None, description="Percentage below horizon.")

    east_count: Optional[int] = Field(default=None, description="Points in eastern hemisphere houses.")
    west_count: Optional[int] = Field(default=None, description="Points in western hemisphere houses.")
    east_pct: Optional[float] = Field(default=None, description="Percentage in eastern hemisphere.")
    west_pct: Optional[float] = Field(default=None, description="Percentage in western hemisphere.")

    counted_points: list[str] = Field(default_factory=list, description="Point names included in the computation.")


class HemispheresModel(BaseModel):
    """Hemispheric emphasis payload."""

    above_below_horizon: HemisphereBreakdownModel = Field(description="Above/below horizon metrics.")
    east_west: HemisphereBreakdownModel = Field(description="East/west hemisphere metrics.")


class LunarMansionModel(BaseModel):
    """Lunar mansion payload for Western 28-equal system."""

    system: Literal["tropical_28_equal"] = Field(description="Lunar mansion system identifier.")
    index: int = Field(description="Lunar mansion index (1-28).")
    start_abs_deg: float = Field(description="Start of mansion interval in absolute degrees.")
    end_abs_deg: float = Field(description="End of mansion interval in absolute degrees.")
    moon_abs_pos: float = Field(description="Moon absolute longitude used for the computation.")


class DerivedNatalProfileModel(BaseModel):
    """Derived natal profile data."""

    chart_ruler: ChartRulerModel
    stelliums: StelliumsModel
    hemispheres: HemispheresModel
    lunar_mansion: LunarMansionModel


class DerivedNatalProfileResponseModel(StatusResponseModel):
    """Response payload for derived natal profile endpoint."""

    subject: AstrologicalSubjectModel = Field(description="Computed astrological subject.")
    derived_profile: DerivedNatalProfileModel = Field(description="Derived profile metrics.")


class ProgressedLunationModel(BaseModel):
    """Progressed lunation payload."""

    angle_deg: float = Field(description="Progressed Sun-Moon angular separation in degrees.")
    phase_name: Literal["New Moon", "First Quarter", "Full Moon", "Last Quarter"] = Field(
        description="Quarter-phase bucket for the progressed lunation."
    )


class ProgressedSignIngressModel(BaseModel):
    """Next progressed Moon sign ingress."""

    at_target_iso_datetime: str = Field(description="Target-timeline datetime where ingress occurs.")
    at_progressed_iso_datetime: str = Field(description="Progressed datetime mapped from target timeline.")
    sign: str = Field(description="Moon sign after ingress.")


class ProgressedHouseIngressModel(BaseModel):
    """Next progressed Moon house ingress."""

    at_target_iso_datetime: str = Field(description="Target-timeline datetime where ingress occurs.")
    at_progressed_iso_datetime: str = Field(description="Progressed datetime mapped from target timeline.")
    house: str = Field(description="Moon house after ingress.")


class ProgressedMoonIngressesModel(BaseModel):
    """Container for next progressed Moon ingress events."""

    next_sign_ingress: Optional[ProgressedSignIngressModel] = None
    next_house_ingress: Optional[ProgressedHouseIngressModel] = None


class ProgressedMoonCycleModel(BaseModel):
    """Secondary progressed Moon cycle payload."""

    target_iso_datetime: str = Field(description="Requested target datetime on the real timeline.")
    progressed_iso_datetime: str = Field(description="Computed progressed datetime.")
    progressed_subject: AstrologicalSubjectModel = Field(description="Progressed chart subject.")
    progressed_lunation: ProgressedLunationModel = Field(description="Progressed lunation details.")
    next_ingresses: ProgressedMoonIngressesModel = Field(description="Upcoming progressed Moon ingress events.")


class ProgressedMoonCycleResponseModel(StatusResponseModel):
    """Response payload for progressed Moon cycle endpoint."""

    progressed_moon_cycle: ProgressedMoonCycleModel


class CompatibilityScoreResponseModel(StatusResponseModel):
    """Response payload for the compatibility score endpoint."""

    score: Optional[float] = Field(
        default=None,
        description="Numeric relationship score.",
    )
    score_description: Optional[str] = Field(
        default=None,
        description="Textual description of the score.",
    )
    is_destiny_sign: Optional[bool] = Field(
        default=None,
        description="Whether the subjects form a destiny-sign relationship.",
    )
    aspects: list[RelationshipScoreAspectModel] = Field(
        default_factory=list,
        description="Aspects considered for the score calculation.",
    )
    score_breakdown: list[ScoreBreakdownItemModel] = Field(
        default_factory=list,
        description="Breakdown of the scoring rules and points contributing to the total score.",
    )
    chart_data: DualChartDataModel = Field(description="Underlying chart data used to compute the score.")


class SubjectContextResponseModel(SubjectResponseModel):
    """Response payload containing a single astrological subject with AI context."""

    subject_context: str = Field(description="AI-optimized context string for the subject.")


class ContextResponseModel(ChartDataResponseModel):
    """Response payload returning chart data with AI-optimized context."""

    context: str = Field(description="AI-optimized context string for the chart data.")


class ReturnContextResponseModel(ContextResponseModel):
    """Response payload for solar and lunar return context requests."""

    return_type: Literal["Solar", "Lunar"] = Field(description="Type of planetary return.")
    wheel_type: Literal["dual", "single"] = Field(description="Rendered wheel configuration.")
