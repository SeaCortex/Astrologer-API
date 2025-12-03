# Solar Return Chart Endpoint

## `POST /api/v5/chart/solar-return`

Generates a Solar Return chart SVG. Can be a single wheel (return only) or dual wheel (natal + return).

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
-   **`return_location`** (object, optional): Relocation.
-   **`wheel_type`** (string, optional): "dual" (default) or "single".
-   **`theme`**, **`language`**, **`split_chart`** (rendering options).

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
    "wheel_type": "dual",
    "theme": "dark"
}
```

### Response Body

-   **`status`** (string): "OK".
-   **`chart_data`** (object): Return data.
-   **`chart`** (string): SVG string.

#### Complete Response Example

```json
{
  "status": "OK",
  "chart_data": { ... },
  "chart": "<svg ...> ... </svg>"
}
```
