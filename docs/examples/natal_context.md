# Natal Chart Context Example

Endpoint: `/api/v5/context/birth-chart`

## Request Body
```json
{
  "subject": {
    "name": "John Doe",
    "year": 1990,
    "month": 1,
    "day": 1,
    "hour": 12,
    "minute": 30,
    "city": "London",
    "nation": "GB",
    "longitude": -0.1278,
    "latitude": 51.5074,
    "timezone": "Europe/London",
    "zodiac_type": "Tropical",
    "houses_system_identifier": "P"
  },
  "theme": "classic"
}
```

## Response Body
```json
{
  "detail": [
    {
      "type": "extra_forbidden",
      "loc": [
        "body",
        "theme"
      ],
      "msg": "Extra inputs are not permitted",
      "input": "classic"
    }
  ]
}
```
