# Subject Context Endpoint

## `POST /api/v5/context/subject`

This endpoint returns an AI-optimized textual description (context) for a given subject. It analyzes the subject's astrological data and provides a coherent summary suitable for feeding into an LLM or displaying to a user.

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
    }
}
```

### Response Body

-   **`status`** (string): "OK".
-   **`subject_context`** (string): The generated text context.
-   **`subject`** (object): The calculated subject data.

#### Complete Response Example

```json
{
  "status": "OK",
  "subject_context": "Subject Name was born on ... The Sun is in Capricorn in the 10th House...",
  "subject": { ... }
}
```
