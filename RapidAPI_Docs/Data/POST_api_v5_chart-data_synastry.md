## Name
Synastry Chart Data

## Description
Returns synastry comparison data between two subjects, including aspects, house comparisons, and optional relationship score, without any SVG rendering. Use this endpoint to analyze relationships in a purely data-driven way.

### Parameters
- `first_subject` (object, required) – primary subject as SubjectModel.
- `second_subject` (object, required) – secondary subject as SubjectModel.
- `include_house_comparison` (bool, optional) – include house comparison information.
- `include_relationship_score` (bool, optional) – compute and return relationship score details.
- `active_points` (array, optional) – active points in the synastry computation.
- `active_aspects` (array, optional) – aspect configuration for inter-chart aspects.
- `distribution_method` (string, optional) – distribution algorithm (`weighted` or `pure_count`).
- `custom_distribution_weights` (object, optional) – custom weights for element and quality distribution.
