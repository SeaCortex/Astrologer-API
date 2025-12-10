## Endpoint
/api/v5/chart/lunar-return

## Name
Lunar (Moon) Return Chart

## Description

Generates a Lunar Return chart for a specific month. The Lunar Return occurs when the Moon returns to the exact position it was at the moment of birth. This chart is used to forecast trends for the month ahead. Returns calculated data and a rendered SVG chart.

### Parameters

-   `subject` (JSON object, required): The subject's natal birth data.
-   `year` (integer, required): The year for the return.
-   `month` (integer, required): The month for the return.
-   `return_location` (JSON object, optional): The location where the subject is for the Lunar Return.
    -   `city` (string, optional)
    -   `nation` (string, optional)
    -   `longitude` (float, required)
    -   `latitude` (float, required)
    -   `timezone` (string, required)
-   `wheel_type` (string, optional): "single" or "dual". Default is "dual".
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
    "month": 11,
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
            "name": "Lunar Return Nov 2024",
            "return_type": "Lunar"
        },
        "aspects": []
    },
    "chart": "<svg>...</svg>"
}
```
