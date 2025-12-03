# Natal Chart Context Endpoint

## `POST /api/v5/context/birth-chart`

Returns AI-optimized context for a full natal chart, including chart data and SVG rendering.

### Request Body

-   **`subject`** (object, required): The subject.
    ```json
    {
        "name": "Subject Name",
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
-   **`theme`**, **`language`**, etc. (rendering options).

#### Complete Request Example

```json
{
    "subject": {
        "name": "Subject Name",
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
    "theme": "classic"
}
```

### Response Body

-   **`status`** (string): "OK".
-   **`context`** (string): The AI context string.
-   **`chart_data`** (object): Chart data.
-   **`chart`** (string): SVG.

#### Complete Response Example

```json
{
  "status": "OK",
  "context": "Natal Chart Analysis for...",
  "chart_data": { ... },
  "chart": "<svg>...</svg>"
}
```
