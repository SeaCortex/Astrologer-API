## Endpoint
/api/v5/chart/solar-return

## Name

Solar Return Chart

## Description

Generates a Solar Return chart for a specific year. The Solar Return occurs when the Sun returns to the exact position it was at the moment of birth. This chart is used to forecast trends for the year ahead. Returns calculated data and a rendered SVG chart (can be single wheel or dual wheel with natal).

### Parameters

-   `subject` (JSON object, required): The subject's natal birth data.
-   `year` (integer, required): The year for which to calculate the Solar Return.
-   `return_location` (JSON object, optional): The location where the subject is for the Solar Return (defaults to birth location if not provided).
    -   `city` (string, optional)
    -   `nation` (string, optional)
    -   `longitude` (float, required)
    -   `latitude` (float, required)
    -   `timezone` (string, required)
-   `wheel_type` (string, optional): "single" (just the return chart) or "dual" (return chart around natal chart). Default is "dual".
-   `theme` (string, optional): Visual theme.
-   `language` (string, optional): Language code.
-   `split_chart` (boolean, optional): Return separate wheel and grid SVGs.
-   `transparent_background` (boolean, optional): Transparent background.
-   `show_house_position_comparison` (boolean, optional): Include house comparison table.
-   `custom_title` (string, optional): Custom title.
-   `active_points` (array, optional): Points to include.
-   `active_aspects` (array, optional): Aspects to include.

## Request Body Example

```json
{
    "subject": {
        "name": "John Doe",
        "year": 1990,
        "month": 6,
        "day": 15,
        "hour": 12,
        "minute": 30,
        "city": "London",
        "nation": "GB",
        "longitude": -0.1278,
        "latitude": 51.5074,
        "timezone": "Europe/London"
    },
    "year": 2024,
    "return_location": {
        "city": "New York",
        "nation": "US",
        "longitude": -74.006,
        "latitude": 40.7128,
        "timezone": "America/New_York"
    },
    "wheel_type": "dual",
    "theme": "classic",
    "language": "EN"
}
```

## Response Body Example

```json
{
    "status": "OK",
    "chart_data": {
        "chart_type": "DualReturnChart",
        "first_subject": {
            "name": "John Doe"
        },
        "second_subject": {
            "name": "Solar Return 2024",
            "return_type": "Solar"
        },
        "aspects": []
    },
    "chart": "<svg>...</svg>"
}
```
