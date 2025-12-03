# Solar Return Context Endpoint

## `POST /api/v5/context/solar-return`

Generates an AI-powered interpretation of a Solar Return chart. The Solar Return occurs once a year when the Sun returns to its exact natal position. This chart is used to forecast the themes and events for the year ahead (from one birthday to the next).

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
        "lng": -0.1278,
        "lat": 51.5074,
        "tz_str": "Europe/London"
    }
    ```
-   **`year`** (integer, required): The year for which to calculate the return (e.g., 2024 for the 2024-2025 birthday year).
-   **`return_location`** (object, optional): Location where the subject spends their birthday (relocation).
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

-   **`status`** (string): "OK" on success.
-   **`context`** (string): The generated AI text interpretation of the solar return.
-   **`chart_data`** (object): The complete calculated solar return chart data.

#### Complete Response Example

```json
{
  "status": "OK",
  "context": "Solar Return Analysis for 2024...\nThe Ascendant of the return chart is in...",
  "chart_data": {
    "natal_subject": { ... },
    "return_subject": { ... },
    "aspects_list": [ ... ]
    // ... full return data
  }
}
```
