# Natal Chart Context Endpoint

## `POST /api/v5/context/birth-chart`

> **📘 [View Complete Example](../examples/natal_context.md)**

Generates an AI-powered interpretation of a full natal chart. Unlike the simple subject context, this endpoint analyzes the complete chart data, including house systems and aspects, providing a deeper and more comprehensive reading of the birth chart's dynamics.

### Request Body

-   **`subject`** (object, required): The subject's birth data.
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
-   **`theme`**, **`language`**, etc. (rendering options, though this endpoint returns data/context, not SVG).

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

-   **`status`** (string): "OK" on success.
-   **`context`** (string): The generated AI text interpretation of the natal chart.
-   **`chart_data`** (object): The complete calculated chart data.

#### Complete Response Example

```json
{
  "status": "OK",
  "context": "Natal Chart Analysis for Subject Name...\nThe Sun is in Capricorn...",
  "chart_data": {
    "subject": { ... },
    "houses_list": [ ... ],
    "aspects_list": [ ... ]
    // ... full chart data
  }
}
```
