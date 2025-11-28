## Name
Lunar Return Chart

## Description
Returns lunar return chart data and a rendered SVG chart for a selected period, including return type and wheel layout. Use this endpoint when you need a visual representation of the Moon’s return relative to the natal chart.

### Parameters
- `subject` (object, required) – natal SubjectModel used as reference.
- `year` (int, optional) – target year for the lunar return.
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
