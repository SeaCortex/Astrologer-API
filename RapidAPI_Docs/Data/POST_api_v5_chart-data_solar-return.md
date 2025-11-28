## Name
Solar Return Data

## Description
Computes solar return chart data for a requested year, month, or instant and returns JSON only, suitable for storage, analysis, or AI pipelines. No SVG rendering is performed by this endpoint.

### Parameters
- `subject` (object, required) – natal SubjectModel used as reference.
- `year` (int, optional) – target year for the solar return.
- `month` (int, optional) – target month when using month+year mode.
- `iso_datetime` (string, optional) – ISO timestamp for an exact return moment.
- `wheel_type` (string, optional) – `"dual"` or `"single"` wheel layout affecting the data model.
- `active_points` (array, optional) – points to include in the return chart data.
- `active_aspects` (array, optional) – aspect configuration used in the computation.
- `distribution_method` (string, optional) – distribution algorithm (`weighted` or `pure_count`).
- `custom_distribution_weights` (object, optional) – custom weights for element and quality distribution.
