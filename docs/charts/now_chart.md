# Now Chart Endpoint

## `POST /api/v5/now/chart`

This endpoint generates a visual chart (SVG) for the **current moment** (UTC at Greenwich). It is useful for displaying the current state of the sky in a visual format.

### Request Body

-   **`name`** (string, optional): Custom name for the chart title (default: "Now").
-   **`zodiac_type`**, **`sidereal_mode`**, **`houses_system_identifier`** (optional configuration).
-   **`theme`**, **`language`**, **`split_chart`**, etc. (rendering options).

#### Complete Request Example

```json
{
    "name": "Current Sky",
    "theme": "light",
    "language": "IT",
    "houses_system_identifier": "W"
}
```

### Response Body

-   **`status`** (string): "OK".
-   **`chart_data`** (object): Calculated data for now.
-   **`chart`** (string): SVG string.

#### Complete Response Example

```json
{
  "status": "OK",
  "chart_data": { ... },
  "chart": "<svg ...> ... </svg>"
}
```
