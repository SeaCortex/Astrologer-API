## Endpoint
/api/v5/chart-data/solar-return

## Name

Solar Return Data

## Description

Calculates Solar Return chart data for a specific year. Does not include SVG rendering.

### Parameters

-   `subject` (JSON object, required): The subject's natal birth data.
-   `year` (integer, required): The year for the return.
-   `return_location` (JSON object, optional): The location where the subject is for the Solar Return.
-   `wheel_type` (string, optional): "single" or "dual".
-   `include_house_comparison` (boolean, optional): Include house comparison table.
-   `active_points` (array, optional): Points to include.
-   `active_aspects` (array, optional): Aspects to include.
-   `distribution_method` (string, optional): Distribution calculation method.

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
    "wheel_type": "dual"
}
```

## Response Body Example

```json
{
    "status": "OK",
    "chart_data": {
        "chart_type": "DualReturnChart",
        "first_subject": { "name": "John Doe" },
        "second_subject": {
            "name": "Solar Return 2024",
            "return_type": "Solar"
        },
        "aspects": []
    }
}
```
