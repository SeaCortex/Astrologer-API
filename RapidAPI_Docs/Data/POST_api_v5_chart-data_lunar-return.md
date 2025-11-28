## Name
Lunar Return Data

## Description
Computes lunar return chart data for a selected period and returns JSON only, exposing the structure of the lunar return without generating an SVG. Use this endpoint for data-centric lunar return workflows.

### Parameters
- `subject` (object, required) – natal SubjectModel used as reference.
- `year` (int, optional) – target year for the lunar return.
- `month` (int, optional) – target month when using month+year mode.
- `iso_datetime` (string, optional) – ISO timestamp for an exact return moment.
- `wheel_type` (string, optional) – `"dual"` or `"single"` wheel layout affecting the data model.
- `active_points` (array, optional) – points to include in the return chart data.
- `active_aspects` (array, optional) – aspect configuration used in the computation.
- `distribution_method` (string, optional) – distribution algorithm (`weighted` or `pure_count`).
- `custom_distribution_weights` (object, optional) – custom weights for element and quality distribution.
