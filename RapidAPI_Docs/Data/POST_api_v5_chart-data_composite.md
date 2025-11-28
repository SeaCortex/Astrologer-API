## Name
Composite Chart Data

## Description
Returns midpoint composite chart data between two subjects, describing the combined chart as structured JSON only. Use this endpoint when you want composite information without generating a visual chart.

### Parameters
- `first_subject` (object, required) – first subject as SubjectModel.
- `second_subject` (object, required) – second subject as SubjectModel.
- `active_points` (array, optional) – active points in the composite chart.
- `active_aspects` (array, optional) – aspect configuration used in the composite.
- `distribution_method` (string, optional) – distribution algorithm (`weighted` or `pure_count`).
- `custom_distribution_weights` (object, optional) – custom weights for element and quality distribution.
