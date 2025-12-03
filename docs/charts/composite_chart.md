# Composite Chart Endpoint

## `POST /api/v5/chart/composite`

Generates a composite chart SVG. This is a single wheel chart representing the midpoint relationship.

### Request Body

-   **`first_subject`** (object, required): First partner.
    ```json
    {
        "name": "Partner A",
        "year": 1980,
        "month": 1,
        "day": 1,
        "hour": 12,
        "minute": 0,
        "city": "Rome",
        "nation": "IT",
        "lng": 12.4964,
        "lat": 41.9028,
        "tz_str": "Europe/Rome"
    }
    ```
-   **`second_subject`** (object, required): Second partner.
    ```json
    {
        "name": "Partner B",
        "year": 1982,
        "month": 3,
        "day": 15,
        "hour": 14,
        "minute": 30,
        "city": "Milan",
        "nation": "IT",
        "lng": 9.19,
        "lat": 45.4642,
        "tz_str": "Europe/Rome"
    }
    ```
-   **`theme`**, **`language`**, **`split_chart`** (rendering options).

#### Complete Request Example

```json
{
    "first_subject": {
        "name": "Partner A",
        "year": 1980,
        "month": 1,
        "day": 1,
        "hour": 12,
        "minute": 0,
        "city": "Rome",
        "nation": "IT",
        "lng": 12.4964,
        "lat": 41.9028,
        "tz_str": "Europe/Rome"
    },
    "second_subject": {
        "name": "Partner B",
        "year": 1982,
        "month": 3,
        "day": 15,
        "hour": 14,
        "minute": 30,
        "city": "Milan",
        "nation": "IT",
        "lng": 9.19,
        "lat": 45.4642,
        "tz_str": "Europe/Rome"
    },
    "theme": "dark"
}
```

### Response Body

-   **`status`** (string): "OK".
-   **`chart_data`** (object): Composite data.
-   **`chart`** (string): SVG string.

#### Complete Response Example

```json
{
  "status": "OK",
  "chart_data": { ... },
  "chart": "<svg ...> ... </svg>"
}
```
