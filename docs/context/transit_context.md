# Transit Context Endpoint

## `POST /api/v5/context/transit`

Returns AI-optimized context for a transit chart.

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
-   **`theme`**, etc.

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
    }
}
```

### Response Body

-   **`status`** (string): "OK".
-   **`context`** (string): Transit analysis context.
-   **`chart_data`** (object): Transit data.
-   **`chart`** (string): SVG.

#### Complete Response Example

```json
{
  "status": "OK",
  "context": "Transit Analysis for...",
  "chart_data": { ... },
  "chart": "<svg>...</svg>"
}
```
