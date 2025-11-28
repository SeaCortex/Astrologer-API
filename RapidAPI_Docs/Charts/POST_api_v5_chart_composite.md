## Name
Composite Chart

## Description
Returns midpoint composite chart data and a rendered SVG chart built from two subjects, using the midpoint method. Use this endpoint when you need a single composite chart that blends two natal charts into one symbolic representation.

### Parameters
- `first_subject` (object, required) – first subject as SubjectModel.
- `second_subject` (object, required) – second subject as SubjectModel.
- `active_points` (array, optional) – points to include in the composite computation.
- `active_aspects` (array, optional) – aspect configuration for the composite chart.
- `distribution_method` (string, optional) – distribution algorithm (`weighted` or `pure_count`).
- `custom_distribution_weights` (object, optional) – custom weights for element and quality distribution.
- `theme` (string, optional) – SVG visual theme.
- `language` (string, optional) – chart language code.
- `split_chart` (bool, optional) – whether to return `chart_wheel` and `chart_grid` separately.
- `transparent_background` (bool, optional) – use transparent background in the SVG.
- `show_house_position_comparison` (bool, optional) – include or exclude house comparison in the SVG.
- `custom_title` (string, optional) – temporary title for the rendered chart.
