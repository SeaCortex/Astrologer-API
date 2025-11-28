## Name
Transit Chart

## Description
Returns transit chart data and a rendered SVG chart showing current or selected transits relative to a natal chart. Use this endpoint to visualize how a transit chart interacts with a base natal subject in SVG form.

### Parameters
- `first_subject` (object, required) – natal SubjectModel used as the base chart.
- `transit_subject` (object, required) – SubjectModel representing the transit moment.
- `include_house_comparison` (bool, optional) – include house comparison tables.
- `active_points` (array, optional) – points to include in the transit analysis.
- `active_aspects` (array, optional) – aspect configuration for transit-to-natal aspects.
- `distribution_method` (string, optional) – distribution algorithm (`weighted` or `pure_count`).
- `custom_distribution_weights` (object, optional) – custom weights for element and quality distribution.
- `theme` (string, optional) – visual theme for the SVG chart.
- `language` (string, optional) – chart language code.
- `split_chart` (bool, optional) – return `chart_wheel` and `chart_grid` separately.
- `transparent_background` (bool, optional) – render SVG with transparent background.
- `show_house_position_comparison` (bool, optional) – include house comparison in the SVG.
- `custom_title` (string, optional) – temporary title for the rendered chart.
