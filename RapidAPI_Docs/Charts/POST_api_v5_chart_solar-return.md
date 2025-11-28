## Name
Solar Return Chart

## Description
Returns solar return chart data and a rendered SVG chart for a given year, month, or instant, including return metadata such as return type and wheel configuration. Use this endpoint when you need both numerical data and a visual chart for solar returns.

### Parameters
- `subject` (object, required) – natal SubjectModel used as reference.
- `year` (int, optional) – target year for the solar return.
- `month` (int, optional) – target month when using month+year mode.
- `iso_datetime` (string, optional) – ISO timestamp for an exact return moment.
- `wheel_type` (string, optional) – `"dual"` or `"single"` wheel layout.
- `active_points` (array, optional) – points to include in the return chart.
- `active_aspects` (array, optional) – aspect configuration for the return chart.
- `distribution_method` (string, optional) – distribution algorithm (`weighted` or `pure_count`).
- `custom_distribution_weights` (object, optional) – custom weights for element and quality distribution.
- `theme` (string, optional) – SVG visual theme.
- `language` (string, optional) – chart language code.
- `split_chart` (bool, optional) – return `chart_wheel` and `chart_grid` instead of a single `chart`.
- `transparent_background` (bool, optional) – render SVG with transparent background.
- `show_house_position_comparison` (bool, optional) – include or hide house comparison.
- `custom_title` (string, optional) – temporary title override for the rendered chart.
