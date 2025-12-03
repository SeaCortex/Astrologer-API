# Now Context Endpoint

## `POST /api/v5/now/context`

This endpoint returns an AI-optimized textual description for the **current moment** (UTC at Greenwich). It describes the current astrological atmosphere, useful for "Daily Horoscope" or "Current Vibes" features.

### Request Body

-   **`name`** (string, optional): Name override.
-   **`zodiac_type`**, **`sidereal_mode`**, etc. (configuration).

#### Complete Request Example

```json
{
    "name": "Current Atmosphere",
    "zodiac_type": "Tropical"
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
  "subject_context": "Current Atmosphere (Now): The Sun is in Scorpio...",
  "subject": { ... }
}
```
