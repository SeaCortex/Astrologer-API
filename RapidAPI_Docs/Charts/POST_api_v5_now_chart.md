## Name
Current UTC Chart

## Description
Returns natal chart data and a rendered SVG chart for the current UTC time in Greenwich, building the subject on-the-fly from “now”. Use this endpoint for real-time charts without providing full birth data.

### Parameters
- `name` (string, optional) – label for the generated subject (default `"Now"`).
- `zodiac_type` (string, optional) – `"Tropical"` or sidereal type.
- `sidereal_mode` (string or null, optional) – sidereal mode when applicable.
- `perspective_type` (string, optional) – perspective type (e.g. `"Apparent Geocentric"`).
- `houses_system_identifier` (string, optional) – house system code (e.g. `"P"`).
- `theme` (string, optional) – SVG visual theme.
- `language` (string, optional) – chart language code.
- `split_chart` (bool, optional) – return `chart_wheel` and `chart_grid` separately.
- `transparent_background` (bool, optional) – render SVG with transparent background.
- `show_house_position_comparison` (bool, optional) – include or hide house comparison.
- `custom_title` (string, optional) – temporary title for the rendered chart.
- `active_points` (array, optional) – active points used in computation.
- `active_aspects` (array, optional) – active aspects and orbs.
- `distribution_method` (string, optional) – distribution algorithm (`weighted` or `pure_count`).
- `custom_distribution_weights` (object, optional) – custom weights for element and quality distribution.
