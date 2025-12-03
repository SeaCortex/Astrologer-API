# Composite Context Endpoint

## `POST /api/v5/context/composite`

Returns AI-optimized context for a composite chart.

### Request Body

-   **`first_subject`** (object, required): First partner.
    ```json
    {
        "name": "Partner A",
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
-   **`second_subject`** (object, required): Second partner.
    ```json
    {
        "name": "Partner B",
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
-   **`theme`**, etc.

#### Complete Request Example

```json
{
    "first_subject": {
        "name": "Partner A",
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
        "name": "Partner B",
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
}
```

### Response Body

-   **`status`** (string): "OK".
-   **`context`** (string): Composite chart analysis context.
-   **`chart_data`** (object): Composite data.
-   **`chart`** (string): SVG.

#### Complete Response Example

```json
{
  "status": "OK",
  "context": "Composite Chart Analysis...",
  "chart_data": { ... },
  "chart": "<svg>...</svg>"
}
```
