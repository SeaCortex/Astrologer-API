## Name
Natal Context

## Description
Returns natal chart data and an AI-optimized textual context string describing the natal chart’s main configurations. Use this endpoint to obtain both structured data and a narrative summary for a single natal chart.

### Parameters
- `subject` (object, required) – SubjectModel with birth data.
- `active_points` (array, optional) – points to include in the analysis.
- `active_aspects` (array, optional) – aspect configuration and orbs.
- `distribution_method` (string, optional) – distribution algorithm (`weighted` or `pure_count`).
- `custom_distribution_weights` (object, optional) – custom weights for element and quality distribution.
