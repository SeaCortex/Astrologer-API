# Solar Return Context Endpoint

## `POST /api/v5/context/solar-return`

Returns AI-optimized context for a solar return chart.

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
-   **`year`** (integer, required): Return year.
-   **`theme`**, etc.

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
    "year": 2024
}
```

### Response Body

-   **`status`** (string): "OK".
-   **`context`** (string): Solar return analysis context.
-   **`chart_data`** (object): Return data.
-   **`chart`** (string): SVG.

#### Complete Response Example

```json
{
  "status": "OK",
  "context": "Solar Return Analysis...",
  "chart_data": { ... },
  "chart": "<svg>...</svg>"
}
```
