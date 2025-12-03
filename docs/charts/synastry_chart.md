# Synastry Chart Endpoint

## `POST /api/v5/chart/synastry`

> **📘 [View Complete Example](../examples/synastry_chart_svg.md)**

Generates a dual-wheel synastry chart SVG. The first subject is placed on the inner wheel, and the second subject on the outer wheel.

### Request Body

-   **`first_subject`** (object, required): Inner wheel subject.
    ```json
    {
        "name": "Inner",
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
-   **`second_subject`** (object, required): Outer wheel subject.
    ```json
    {
        "name": "Outer",
        "year": 1992,
        "month": 5,
        "day": 15,
        "hour": 18,
        "minute": 30,
        "city": "New York",
        "nation": "US",
        "lng": -74.006,
        "lat": 40.7128,
        "tz_str": "America/New_York"
    }
    ```
-   **`theme`**, **`language`**, **`split_chart`** (rendering options).
-   **`show_house_position_comparison`** (bool, optional): Display house table (default: true).

#### Complete Request Example

```json
{
    "first_subject": {
        "name": "Inner",
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
    "second_subject": {
        "name": "Outer",
        "year": 1992,
        "month": 5,
        "day": 15,
        "hour": 18,
        "minute": 30,
        "city": "New York",
        "nation": "US",
        "lng": -74.006,
        "lat": 40.7128,
        "tz_str": "America/New_York"
    },
    "theme": "classic",
    "split_chart": true
}
```

### Response Body

-   **`status`** (string): "OK".
-   **`chart_data`** (object): Synastry data.
-   **`chart_wheel`** (string): SVG of the dual wheel.
-   **`chart_grid`** (string): SVG of the aspect grid.

#### Complete Response Example

```json
{
  "status": "OK",
  "chart_data": { ... },
  "chart_wheel": "<svg ...> ... </svg>",
  "chart_grid": "<svg ...> ... </svg>"
}
```
