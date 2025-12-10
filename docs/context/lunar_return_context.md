---
title: 'Lunar Return Context'
order: 8
---

# Lunar Return Context Endpoint

## `POST /api/v5/context/lunar-return`

> **📘 [View Complete Example](../examples/lunar_return_context.md)**

Generates an AI-powered interpretation of a Lunar Return chart. The Lunar Return occurs roughly every 28 days when the Moon returns to its exact natal position. This chart is used to forecast the emotional themes and events for the coming month.

### Request Body

-   **`subject`** (object, required): The Natal Subject.
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
-   **`year`** (integer, required): The year of the return.
-   **`month`** (integer, required): The month of the return.
-   **`return_location`** (object, optional): Relocation for the return.
-   **Computation options**: `active_points`, `active_aspects`, `distribution_method`, `custom_distribution_weights` (identical to `/api/v5/chart-data/lunar-return`). Rendering options such as `theme`, `language`, `split_chart`, `transparent_background`, `show_house_position_comparison`, `show_cusp_position_comparison`, `show_degree_indicators`, `custom_title` are **not** accepted here.

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
    "month": 5
}
```

### Response Body

-   **`status`** (string): "OK" on success.
-   **`context`** (string): The generated AI text interpretation of the lunar return.
-   **`chart_data`** (object): The complete calculated lunar return chart data.

#### Complete Response Example

```json
{
  "status": "OK",
  "context": "Lunar Return Analysis for May 2024...\nThe Moon is in the 4th House...",
  "chart_data": {
    "natal_subject": { ... },
    "return_subject": { ... },
    "aspects_list": [ ... ]
    // ... full return data
  }
}
```
