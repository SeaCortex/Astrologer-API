# Natal Chart Endpoint

## `POST /api/v5/chart/birth-chart`

> **📘 [View Complete Example](../examples/natal_chart_svg.md)**

This endpoint generates a visual birth chart (SVG) along with the calculated astrological data. It supports various customization options for the chart's appearance.

### Request Body

-   **`subject`** (object, required): The subject's birth data.
    ```json
    {
        "name": "Alice",
        "year": 1995,
        "month": 6,
        "day": 15,
        "hour": 14,
        "minute": 30,
        "city": "Berlin",
        "nation": "DE",
        "lng": 13.405,
        "lat": 52.52,
        "tz_str": "Europe/Berlin"
    }
    ```
-   **`theme`** (string, optional): Color theme for the chart (e.g., "classic", "dark", "high_contrast"). Default: "classic".
-   **`language`** (string, optional): Language for chart labels (e.g., "EN", "IT", "ES"). Default: "EN".
-   **`split_chart`** (bool, optional): If true, returns the chart wheel and aspect grid as separate SVG strings. Default: false.
-   **`transparent_background`** (bool, optional): If true, the chart background will be transparent. Default: false.
-   **`custom_title`** (string, optional): Override the default chart title.

#### Complete Request Example

```json
{
    "subject": {
        "name": "Alice",
        "year": 1995,
        "month": 6,
        "day": 15,
        "hour": 14,
        "minute": 30,
        "city": "Berlin",
        "nation": "DE",
        "lng": 13.405,
        "lat": 52.52,
        "tz_str": "Europe/Berlin"
    },
    "theme": "dark",
    "language": "EN",
    "split_chart": false,
    "transparent_background": true
}
```

### Response Body

-   **`status`** (string): "OK".
-   **`chart_data`** (object): The calculated chart data (same as chart-data endpoint).
-   **`chart`** (string): The full SVG string of the chart (if `split_chart` is false).
-   **`chart_wheel`** (string): SVG of the wheel (if `split_chart` is true).
-   **`chart_grid`** (string): SVG of the aspect grid (if `split_chart` is true).

#### Complete Response Example

```json
{
  "status": "OK",
  "chart_data": { ... },
  "chart": "<svg xmlns='http://www.w3.org/2000/svg' ...> ... </svg>"
}
```
