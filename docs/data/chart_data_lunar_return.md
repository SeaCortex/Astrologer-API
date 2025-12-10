---
title: 'Lunar Return Chart Data'
order: 9
---

# Lunar Return Chart Data Endpoint

## `POST /api/v5/chart-data/lunar-return`

> **📘 [View Complete Example](../examples/lunar_return_chart_data.md)**

Calculates the Lunar Return chart for a given month/year. The Lunar Return occurs when the Moon returns to the exact same position as in the natal chart (happens every ~27 days).

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
        "longitude": -0.1278,
        "latitude": 51.5074,
        "timezone": "Europe/London"
    }
    ```
-   **`year`** (integer, required): Year to search.
-   **`month`** (integer, required): Month to search.
-   **`return_location`** (object, optional): Relocation for the return.
-   **`wheel_type`** (string, optional): "dual" or "single".

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
    "wheel_type": "single"
}
```

### Response Body

-   **`status`** (string): "OK".
-   **`return_type`** (string): "Lunar".
-   **`wheel_type`** (string): "single".
-   **`chart_data`** (object): Single chart data (since wheel_type is single).

#### Complete Response Example

```json
{
  "status": "OK",
  "return_type": "Lunar",
  "wheel_type": "single",
  "chart_data": {
    "planets": { ... },
    "houses": [ ... ],
    "aspects": [ ... ]
  }
}
```
