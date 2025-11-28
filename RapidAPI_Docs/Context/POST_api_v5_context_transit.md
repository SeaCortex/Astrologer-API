## Name
Transit Context

## Description
Returns transit chart data and an AI-optimized textual context explaining transit influences relative to a natal chart. Use this endpoint when you require both structured transit data and a descriptive summary.

### Parameters
- `first_subject` (object, required) – natal SubjectModel used as base chart.
- `transit_subject` (object, required) – SubjectModel for the transit moment.
- `include_house_comparison` (bool, optional) – include house comparison information.
- `active_points` (array, optional) – active points in the transit analysis.
- `active_aspects` (array, optional) – aspect configuration for transit-to-natal aspects.
- `distribution_method` (string, optional) – distribution algorithm (`weighted` or `pure_count`).
- `custom_distribution_weights` (object, optional) – custom weights for element and quality distribution.
