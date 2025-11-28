## Name
Synastry Context

## Description
Returns synastry chart data and an AI-optimized textual context describing the relationship between two subjects. Use this endpoint when you need a narrative explanation of synastry dynamics for AI or human consumption.

### Parameters
- `first_subject` (object, required) – primary subject as SubjectModel.
- `second_subject` (object, required) – secondary subject as SubjectModel.
- `include_house_comparison` (bool, optional) – include house comparison in the data.
- `include_relationship_score` (bool, optional) – include relationship score information.
- `active_points` (array, optional) – active points used in computation.
- `active_aspects` (array, optional) – aspect configuration for inter-chart aspects.
- `distribution_method` (string, optional) – distribution algorithm (`weighted` or `pure_count`).
- `custom_distribution_weights` (object, optional) – custom weights for element and quality distribution.
