## Name
Solar Return Context

## Description
Returns solar return chart data and an AI-optimized textual context summarizing the solar return configuration, including return type and wheel layout information. Use this endpoint for narrative-ready solar return analysis.

### Parameters
- `subject` (object, required) – natal SubjectModel used as reference.
- `year` (int, optional) – target year for the solar return.
- `month` (int, optional) – target month when using month+year mode.
- `iso_datetime` (string, optional) – ISO timestamp for an exact return moment.
- `wheel_type` (string, optional) – `"dual"` or `"single"` wheel layout affecting the data.
- `active_points` (array, optional) – points included in the return chart data.
- `active_aspects` (array, optional) – aspect configuration used in the computation.
- `distribution_method` (string, optional) – distribution algorithm (`weighted` or `pure_count`).
- `custom_distribution_weights` (object, optional) – custom weights for element and quality distribution.
