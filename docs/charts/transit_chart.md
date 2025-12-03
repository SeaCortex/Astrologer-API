# Transit Chart Endpoint

## `POST /api/v5/chart/transit`

> **📘 [View Complete Example](../examples/transit_chart_svg.md)**

Generates a transit chart SVG (dual wheel). Inner wheel is the natal chart, outer wheel is the transit chart.

### Request Body

-   **`first_subject`** (object, required): Natal subject.
    ```json
    {
        "name": "Natal Subject",
        "year": 1990,
        "month": 1,
        "day": 1,
        "hour": 12,
        "minute": 0,
        "city": "London",
        "nation": "GB",
        "lng": -0.1278,
        "lat": 51.5074,
        "tz_str": "Europe/London"
    }
    ```
-   **`transit_subject`** (object, required): Transit moment.
    ```json
    {
        "name": "Transit Moment",
        "year": 2024,
        "month": 1,
        "day": 1,
        "hour": 0,
        "minute": 0,
        "city": "London",
        "nation": "GB",
        "lng": -0.1278,
        "lat": 51.5074,
        "tz_str": "Europe/London"
    }
    ```
-   **`theme`**, **`language`**, **`split_chart`** (rendering options).

#### Complete Request Example

```json
{
    "first_subject": {
        "name": "Natal Subject",
        "year": 1990,
        "month": 1,
        "day": 1,
        "hour": 12,
        "minute": 0,
        "city": "London",
        "nation": "GB",
        "lng": -0.1278,
        "lat": 51.5074,
        "tz_str": "Europe/London"
    },
    "transit_subject": {
        "name": "Transit Moment",
        "year": 2024,
        "month": 1,
        "day": 1,
        "hour": 0,
        "minute": 0,
        "city": "London",
        "nation": "GB",
        "lng": -0.1278,
        "lat": 51.5074,
        "tz_str": "Europe/London"
    },
    "theme": "classic"
}
```

### Response Body

-   **`status`** (string): "OK".
-   **`chart_data`** (object): Transit data.
-   **`chart`** (string): SVG string.

#### Complete Response Example

```json
{
  "status": "OK",
  "chart_data": { ... },
  "chart": "<svg ...> ... </svg>"
}
```
