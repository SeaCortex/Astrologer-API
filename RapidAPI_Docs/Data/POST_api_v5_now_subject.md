## Name
Current UTC Subject

## Description
Returns an astrological subject computed for the current UTC time in Greenwich, using minimal configuration parameters. Use this endpoint when you need a “now” subject without specifying full birth data.

### Parameters
- `name` (string, optional) – label for the generated subject (default `"Now"`).
- `zodiac_type` (string, optional) – `"Tropical"` or sidereal type.
- `sidereal_mode` (string or null, optional) – sidereal mode when applicable.
- `perspective_type` (string, optional) – perspective type (e.g. `"Apparent Geocentric"`).
- `houses_system_identifier` (string, optional) – house system code (e.g. `"P"`).
