## Name
Lunar Return Context

## Description
Returns lunar return chart data and an AI-optimized textual context summarizing the lunar return configuration. Use this endpoint when you need a descriptive lunar return analysis alongside structured data.

### Parameters
- `subject` (object, required) – natal SubjectModel used as reference.
- `year` (int, optional) – target year for the lunar return.
- `month` (int, optional) – target month when using month+year mode.
- `iso_datetime` (string, optional) – ISO timestamp for an exact return moment.
- `wheel_type` (string, optional) – `"dual"` or `"single"` wheel layout affecting the data.
- `active_points` (array, optional) – points included in the return chart data.
- `active_aspects` (array, optional) – aspect configuration used in the computation.
- `distribution_method` (string, optional) – distribution algorithm (`weighted` or `pure_count`).
- `custom_distribution_weights` (object, optional) – custom weights for element and quality distribution.
