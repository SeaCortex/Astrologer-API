## Name
UTC Birth Chart

## Description
Returns natal chart data and a rendered SVG chart for a single subject, including visual configuration and computation options. Use this endpoint when you need both machine-readable chart data and a ready-to-display SVG wheel (optionally split into wheel and grid).

### Parameters
- `subject` (object, required) – full birth data as SubjectModel.
- `theme` (string, optional) – chart visual theme (e.g. `classic`, `dark`).
- `language` (string, optional) – chart language code (e.g. `EN`, `IT`).
- `split_chart` (bool, optional) – return separate `chart_wheel` and `chart_grid` instead of a single `chart`.
- `transparent_background` (bool, optional) – render SVG with transparent background.
- `show_house_position_comparison` (bool, optional) – include or hide the house comparison table.
- `custom_title` (string, optional) – temporary chart title override (max 40 characters).
- `active_points` (array, optional) – list of points to include in the computation.
- `active_aspects` (array, optional) – aspect configuration with allowed aspects and orbs.
- `distribution_method` (string, optional) – distribution algorithm (`weighted` or `pure_count`).
- `custom_distribution_weights` (object, optional) – custom weights for element and quality distribution.
