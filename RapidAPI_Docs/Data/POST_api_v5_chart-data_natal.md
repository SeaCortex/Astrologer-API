## Name
Natal Chart Data

## Description
Returns complete natal chart data as JSON for a single subject, including aspects, distributions, and active points, without any SVG rendering. Use this endpoint when you only need structured data for analysis or AI consumption.

### Parameters
- `subject` (object, required) – SubjectModel with full birth data.
- `active_points` (array, optional) – points to include in the natal chart.
- `active_aspects` (array, optional) – aspect configuration and orbs.
- `distribution_method` (string, optional) – distribution algorithm (`weighted` or `pure_count`).
- `custom_distribution_weights` (object, optional) – custom weights for element and quality distribution.
