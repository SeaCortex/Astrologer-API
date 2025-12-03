# Solar Return Chart Data Endpoint

## `POST /api/v5/chart-data/solar-return`

> **📘 [View Complete Example](../examples/solar_return_chart_data.md)**

Calculates the Solar Return chart for a given year. The Solar Return occurs when the Sun returns to the exact same position (longitude) as in the natal chart.

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
-   **`year`** (integer, required): The year for which to calculate the return.
-   **`return_location`** (object, optional): Location where the subject spends the return (relocation). If omitted, uses natal location.
-   **`wheel_type`** (string, optional): "dual" (default) or "single".
    -   "dual": Returns both natal and return charts (bi-wheel data).
    -   "single": Returns only the return chart.

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
    "return_location": {
        "city": "Paris",
        "nation": "FR",
        "lng": 2.3522,
        "lat": 48.8566,
        "tz_str": "Europe/Paris"
    }
}
```

### Response Body

-   **`status`** (string): "OK".
-   **`return_type`** (string): "Solar".
-   **`wheel_type`** (string): "dual" or "single".
-   **`chart_data`** (object): Single or Dual chart data structure.

#### Complete Response Example

```json
{
  "status": "OK",
  "return_type": "Solar",
  "wheel_type": "dual",
  "chart_data": {
    "first_subject": { ... }, // Natal
    "second_subject": { ... }, // Solar Return
    "aspects": [ ... ]
  }
}
```
