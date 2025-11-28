## Name
Current Moment Context

## Description
Returns an astrological subject and AI-optimized context for the current UTC time in Greenwich, built without requiring full birth data. Use this endpoint when you need a real-time textual description of the current sky.

### Parameters
- `name` (string, optional) – label for the generated subject (default `"Now"`).
- `zodiac_type` (string, optional) – `"Tropical"` or sidereal type.
- `sidereal_mode` (string or null, optional) – sidereal mode when applicable.
- `perspective_type` (string, optional) – perspective type (e.g. `"Apparent Geocentric"`).
- `houses_system_identifier` (string, optional) – house system code (e.g. `"P"`).
