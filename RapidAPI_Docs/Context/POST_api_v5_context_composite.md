## Name
Composite Context

## Description
Returns composite chart data and an AI-optimized textual context describing the midpoint composite chart. Use this endpoint to pair composite JSON data with a ready-to-use narrative summary.

### Parameters
- `first_subject` (object, required) – first subject as SubjectModel.
- `second_subject` (object, required) – second subject as SubjectModel.
- `active_points` (array, optional) – active points in the composite chart.
- `active_aspects` (array, optional) – aspect configuration used in the composite analysis.
- `distribution_method` (string, optional) – distribution algorithm (`weighted` or `pure_count`).
- `custom_distribution_weights` (object, optional) – custom weights for element and quality distribution.
