## Name
Synastry Chart

## Description
Returns synastry chart data and a dual-wheel SVG chart comparing two subjects, including relationship scoring and house comparison options. Use this endpoint to visualize how two natal charts interact in a single, combined SVG.

### Parameters
- `first_subject` (object, required) – primary subject as SubjectModel.
- `second_subject` (object, required) – secondary subject as SubjectModel.
- `include_house_comparison` (bool, optional) – include house comparison tables in the data.
- `include_relationship_score` (bool, optional) – compute and include relationship score details.
- `active_points` (array, optional) – list of chart points to consider.
- `active_aspects` (array, optional) – configuration for aspects and orbs.
- `distribution_method` (string, optional) – distribution algorithm (`weighted` or `pure_count`).
- `custom_distribution_weights` (object, optional) – custom weights for element and quality distribution.
- `theme` (string, optional) – visual theme for the SVG chart.
- `language` (string, optional) – chart language code.
- `split_chart` (bool, optional) – return `chart_wheel` and `chart_grid` separately.
- `transparent_background` (bool, optional) – render the SVG with transparent background.
- `show_house_position_comparison` (bool, optional) – show or hide house comparison in the SVG.
- `custom_title` (string, optional) – temporary title override for the rendered chart.
