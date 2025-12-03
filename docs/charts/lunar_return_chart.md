# Lunar Return Chart Endpoint

## `POST /api/v5/chart/lunar-return`

> **📘 [View Complete Example](../examples/lunar_return_chart_svg.md)**

Generates a Lunar Return chart SVG.

### Request Body

-   **`subject`** (object, required): Natal subject.
    ```json
    {
        "name": "John Doe",
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
-   **`year`** (integer, required): Year.
-   **`month`** (integer, required): Month.
-   **`wheel_type`** (string, optional): "dual" or "single".
-   **`theme`**, **`language`**, **`split_chart`** (rendering options).

#### Complete Request Example

```json
{
    "subject": {
        "name": "John Doe",
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
    "year": 2024,
    "month": 5,
    "wheel_type": "single",
    "theme": "light"
}
```

### Response Body

-   **`status`** (string): "OK".
-   **`chart_data`** (object): Return data.
-   **`chart`** (string): SVG string.

#### Complete Response Example

```json
{
  "status": "OK",
  "chart_data": { ... },
  "chart": "<svg ...> ... </svg>"
}
```
