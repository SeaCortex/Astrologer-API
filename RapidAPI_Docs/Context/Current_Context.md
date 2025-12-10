## Name
UTC Current Date Time Birth - AI Context

## Description

Returns a structured text analysis of the current moment (Now) at Greenwich, optimized for AI/LLMs.

### Parameters

-   `name` (string, optional): Name for the subject (default "Now").
-   `zodiac_type` (string, optional): "Tropical" or "Sidereal".
-   `sidereal_mode` (string, optional): Sidereal mode.
-   `perspective_type` (string, optional): "Apparent Geocentric" or "Heliocentric".
-   `houses_system_identifier` (string, optional): House system code.

## Request Body Example

```json
{
    "name": "Now",
    "zodiac_type": "Tropical"
}
```

## Response Body Example

```json
{
    "status": "OK",
    "subject_context": "Chart for \"Now\"\n...",
    "subject": {
        "name": "Now"
    }
}
```
