## Name
Compatibility Score

## Description
Computes the Ciro Discepolo compatibility score between two subjects, returning a numeric score, qualitative description, and supporting aspect data. Use this endpoint when you need a focused relationship metric rather than a full SVG chart.

### Parameters
- `first_subject` (object, required) – first subject as SubjectModel.
- `second_subject` (object, required) – second subject as SubjectModel.
- `active_points` (array, optional) – points used in compatibility analysis.
- `active_aspects` (array, optional) – aspect configuration influencing the score.
