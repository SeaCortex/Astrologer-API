# Astrologer API v5 Endpoints

This document describes the v5 REST API endpoints for the Astrologer API. All
endpoints accept JSON payloads and return JSON responses.

## Local Development

### Running the API Locally

For local testing and development, run the API in development mode (HMAC
authentication disabled):

```bash
ENV_TYPE=dev uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Once running, access:

- **Swagger UI (Interactive API Docs)**: http://localhost:8000/docs
- **ReDoc (API Reference)**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/health

**Note**: In development mode (`ENV_TYPE=dev`), HMAC authentication is disabled,
so you can test endpoints directly from the Swagger UI without signing requests.

## Base URL

```
http://localhost:8000
```

## Authentication

All requests require the following headers:

```
X-Timestamp: <unix_seconds>
X-Signature: <hex_or_base64_hmac>
```

Signature string (HMAC-SHA256):

```
{timestamp}\n{method}\n{pathWithQuery}\n{sha256(body)}
```

## Common Request Parameters

### Subject Model

Used across most endpoints to define a person's birth data:

```json
{
  "name": "John Doe",
  "year": 1990,
  "month": 6,
  "day": 15,
  "hour": 12,
  "minute": 30,
  "second": 0,
  "city": "London",
  "nation": "GB",
  "timezone": "Europe/London",
  "longitude": -0.1278,
  "latitude": 51.5074,
  "altitude": null,
  "zodiac_type": "Tropical",
  "sidereal_mode": null,
  "perspective_type": "Apparent Geocentric",
  "houses_system_identifier": "P",
  "is_dst": null,
  "geonames_username": null
}
```

**Location Options:**

- Provide `longitude`, `latitude`, and `timezone` for offline mode (recommended)
- OR provide `geonames_username` to use GeoNames API for location lookup
  (requires city and nation)

### Chart Configuration Options

Available for `/charts/*` endpoints and `/api/v5/now/chart` (with SVG
rendering):

- `theme`: Visual theme ("classic", "dark", "light", "strawberry",
  "dark-high-contrast", "black-and-white")
- `language`: Chart language ("EN", "IT", "FR", "ES", "PT", "CN", "RU", "TR",
  "DE", "HI")
- `split_chart`: Boolean - return separate `chart_wheel` and `chart_grid` SVG
  strings (default: false)
- `transparent_background`: Boolean - render chart with transparent background
  instead of theme default
- `show_house_position_comparison`: Boolean - include the house comparison table
  (set to false to hide it and widen the chart)
- `show_cusp_position_comparison`: Boolean - include the cusp position
  comparison table for dual charts (default: true)
- `show_degree_indicators`: Boolean - display radial lines and degree numbers
  for planet positions on the chart wheel (default: true)
- `show_aspect_icons`: Boolean - display aspect icons on aspect lines (default:
  true)
- `custom_title`: String ≤40 chars - temporary override for the rendered chart
  title (trimmed if blank)

### Computation Configuration Options

Available for **all** chart endpoints (both `/chart-data/*` and `/chart/*`):

- `active_points`: Array of points to include (default: all major planets and
  points)
- `active_aspects`: Array of aspect configurations with orbs
- `distribution_method`: "weighted" (default) or "pure_count"
- `custom_distribution_weights`: Custom weight mapping for element/quality
  distribution

**Note:** `/chart-data/*` endpoints return data only (no SVG) and do **not**
accept rendering parameters (`theme`, `language`, `split_chart`,
`transparent_background`, `show_house_position_comparison`,
`show_cusp_position_comparison`, `show_degree_indicators`, `show_aspect_icons`,
`custom_title`). These parameters will be rejected with a 422 error if provided.

## Endpoints

### Health Check

**GET** `/api/v5/health`

Returns API health status.

**Response:**

```json
{
  "status": "OK"
}
```

---

### Current Moment

#### Get Current Subject

**POST** `/api/v5/now/subject`

Returns astrological data for the current UTC time at Greenwich with optional
configuration.

**Request:**

```json
{
  "name": "Now",
  "zodiac_type": "Tropical",
  "sidereal_mode": null,
  "perspective_type": "Apparent Geocentric",
  "houses_system_identifier": "P"
}
```

**Note:** All fields are optional. If not provided, defaults will be used
(name="Now", zodiac_type="Tropical", perspective_type="Apparent Geocentric",
houses_system_identifier="P").

**Response:**

```json
{
  "status": "OK",
  "subject": {
    /* AstrologicalSubjectModel */
  }
}
```

#### Get Current Chart

**POST** `/api/v5/now/chart`

Returns chart data and SVG for the current UTC time at Greenwich with optional
subject and rendering configuration.

**Request:**

```json
{
  "name": "Now",
  "zodiac_type": "Tropical",
  "sidereal_mode": null,
  "perspective_type": "Apparent Geocentric",
  "houses_system_identifier": "P",
  "theme": "classic",
  "language": "EN",
  "split_chart": false,
  "transparent_background": false,
  "show_house_position_comparison": true,
  "show_cusp_position_comparison": true,
  "show_degree_indicators": true,
  "show_aspect_icons": true,
  "custom_title": null,
  "active_points": [...],
  "active_aspects": [...]
}
```

**Note:** All fields are optional. Subject configuration (name, zodiac_type,
etc.) defaults to "Now" with Tropical zodiac. Rendering and computation options
follow the standard chart configuration rules.

**Response:**

```json
{
  "status": "OK",
  "chart_data": {
    /* ChartDataModel */
  },
  "chart": "<svg>...</svg>"
}
```

---

### Subject Data

**POST** `/api/v5/subject`

Returns astrological subject data without chart rendering.

**Request:**

```json
{
  "subject": {
    /* SubjectModel */
  }
}
```

**Response:**

```json
{
  "status": "OK",
  "subject": {
    /* AstrologicalSubjectModel */
  }
}
```

---

### Derived Data

#### Derived Natal Profile

**POST** `/api/v5/derived/natal-profile`

Returns **derived Western-astrology natal metrics** computed from a natal
subject (no SVG).

Includes:

- Chart ruler (traditional rulership, based on Ascendant sign)
- Stelliums (by sign and by house; default min count = 3)
- Hemispheric emphasis (above/below horizon, east/west; computed from counted
  points)
- Lunar mansion (Western **tropical 28-equal** system based on Moon longitude)

**Request:**

```json
{
  "subject": { /* SubjectModel */ },
  "active_points": ["Sun", "Moon", "Mercury", ...]
}
```

**Response:**

```json
{
  "status": "OK",
  "subject": {/* AstrologicalSubjectModel */},
  "derived_profile": {
    "chart_ruler": {
      "asc_sign": "Ar",
      "ruler_point_name": "Mars",
      "ruler_point": {/* KerykeionPointModel (if present in subject) */}
    },
    "stelliums": {
      "min_count": 3,
      "by_sign": [{ "sign": "Ar", "points": ["Sun", "Mercury", "Venus"] }],
      "by_house": [{ "house": "1", "points": ["Sun", "Mercury", "Venus"] }]
    },
    "hemispheres": {
      "above_below_horizon": {
        "above_count": 4,
        "below_count": 6,
        "above_pct": 40.0,
        "below_pct": 60.0,
        "counted_points": ["Sun", "Moon", "Mercury"]
      },
      "east_west": {
        "east_count": 7,
        "west_count": 3,
        "east_pct": 70.0,
        "west_pct": 30.0,
        "counted_points": ["Sun", "Moon", "Mercury"]
      }
    },
    "lunar_mansion": {
      "system": "tropical_28_equal",
      "index": 12,
      "start_abs_deg": 141.4285714286,
      "end_abs_deg": 154.2857142857,
      "moon_abs_pos": 149.12
    }
  }
}
```

---

### Natal Charts

#### Natal Chart Data

**POST** `/api/v5/chart-data/birth-chart`

Returns complete natal chart data without SVG rendering.

**Request:**

```json
{
  "subject": { /* SubjectModel */ },
  "active_points": ["Sun", "Moon", "Mercury", ...],
  "active_aspects": [{"name": "conjunction", "orb": 10}, ...],
  "distribution_method": "weighted",
  "custom_distribution_weights": {"sun": 3.0, "moon": 2.5}
}
```

**Note:** This endpoint does **not** accept rendering parameters (`theme`,
`language`, `split_chart`, `transparent_background`,
`show_house_position_comparison`, `show_cusp_position_comparison`,
`show_degree_indicators`, `show_aspect_icons`, `custom_title`).

**Response:**

```json
{
  "status": "OK",
  "chart_data": {
    "chart_type": "Natal",
    "subject": { /* AstrologicalSubjectModel */ },
    "aspects": [ /* Filtered aspects */ ],
    "element_distribution": {
      "fire": 5.0,
      "earth": 3.5,
      "air": 4.0,
      "water": 2.5,
      "fire_percentage": 33,
      "earth_percentage": 23,
      "air_percentage": 27,
      "water_percentage": 17
    },
    "quality_distribution": {
      "cardinal": 4.0,
      "fixed": 6.0,
      "mutable": 5.0,
      "cardinal_percentage": 27,
      "fixed_percentage": 40,
      "mutable_percentage": 33
    },
    "active_points": [...],
    "active_aspects": [...]
  }
}
```

#### Natal Chart with SVG

**POST** `/api/v5/chart/birth-chart`

Returns natal chart data and rendered SVG chart.

**Request:**

```json
{
  "subject": { /* SubjectModel */ },
  "theme": "classic",
  "language": "EN",
  "split_chart": false,
  "transparent_background": false,
  "show_house_position_comparison": true,
  "show_cusp_position_comparison": true,
  "show_degree_indicators": true,
  "show_aspect_icons": true,
  "custom_title": null,
  "active_points": [...],
  "active_aspects": [...],
  "distribution_method": "weighted",
  "custom_distribution_weights": {}
}
```

**Response:**

```json
{
  "status": "OK",
  "chart_data": {
    /* Same as chart-data endpoint */
  },
  "chart": "<svg>...</svg>"
}
```

---

### Synastry Charts

#### Synastry Chart Data

**POST** `/api/v5/chart-data/synastry`

Returns synastry comparison data between two subjects.

**Request:**

```json
{
  "first_subject": { /* SubjectModel */ },
  "second_subject": { /* SubjectModel */ },
  "include_house_comparison": true,
  "include_relationship_score": true,
  "active_points": [...],
  "active_aspects": [...],
  "distribution_method": "weighted",
  "custom_distribution_weights": {}
}
```

**Note:** This endpoint does **not** accept rendering parameters (`theme`,
`language`, `split_chart`, `transparent_background`,
`show_house_position_comparison`, `show_cusp_position_comparison`,
`show_degree_indicators`, `show_aspect_icons`, `custom_title`).

**Response:**

```json
{
  "status": "OK",
  "chart_data": {
    "chart_type": "Synastry",
    "first_subject": { /* AstrologicalSubjectModel */ },
    "second_subject": { /* AstrologicalSubjectModel */ },
    "aspects": [ /* Inter-chart aspects */ ],
    "house_comparison": {
      "first_points_in_second_houses": [...],
      "second_points_in_first_houses": [...]
    },
    "relationship_score": {
      "score_value": 18,
      "score_description": "Very Important",
      "is_destiny_sign": true,
      "score_breakdown": [
        {
          "rule": "sun_moon_conjunction",
          "description": "Sun-Moon conjunction (high precision)",
          "points": 11,
          "details": "Sun-Moon conjunction (orbit: 1.34°)"
        }
      ],
      "aspects": [...]
    },
    "element_distribution": { /* Combined distribution */ },
    "quality_distribution": { /* Combined distribution */ },
    "active_points": [...],
    "active_aspects": [...]
  }
}
```

#### Synastry Chart with SVG

**POST** `/api/v5/chart/synastry`

Returns synastry data and rendered dual-wheel chart.

**Request:** Same as `/api/v5/chart-data/synastry` plus `theme`, `language`,
`split_chart`, `transparent_background`, `show_house_position_comparison`,
`show_cusp_position_comparison`, `show_degree_indicators`, `show_aspect_icons`,
`custom_title`

**Response:** Same as chart-data endpoint plus `"chart": "<svg>...</svg>"` (or
`"chart_wheel"` and `"chart_grid"` if split_chart=true)

---

### Transit Charts

#### Transit Chart Data

**POST** `/api/v5/chart-data/transit`

Returns transit analysis for current planetary positions affecting a natal
chart.

**Request:**

```json
{
  "first_subject": { /* Natal SubjectModel */ },
  "transit_subject": {
    "name": "Transit",
    "year": 2024,
    "month": 10,
    "day": 27,
    "hour": 12,
    "minute": 0,
    "city": "London",
    "nation": "GB",
    "timezone": "Europe/London",
    "longitude": -0.1278,
    "latitude": 51.5074
  },
  "include_house_comparison": true,
  "active_points": [...],
  "active_aspects": [...],
  "distribution_method": "weighted"
}
```

**Note:** This endpoint does **not** accept rendering parameters (`theme`,
`language`, `split_chart`, `transparent_background`,
`show_house_position_comparison`, `show_cusp_position_comparison`,
`show_degree_indicators`, `show_aspect_icons`, `custom_title`).

**Response:**

```json
{
  "status": "OK",
  "chart_data": {
    "chart_type": "Transit",
    "first_subject": { /* Natal subject */ },
    "second_subject": { /* Transit subject */ },
    "aspects": [ /* Transit-to-natal aspects */ ],
    "house_comparison": {
      "first_points_in_second_houses": [...],
      "second_points_in_first_houses": [...]
    },
    "element_distribution": { /* Combined */ },
    "quality_distribution": { /* Combined */ },
    "active_points": [...],
    "active_aspects": [...]
  }
}
```

#### Transit Chart with SVG

**POST** `/api/v5/chart/transit`

Returns transit data and rendered chart.

**Request:** Same as `/api/v5/chart-data/transit` plus `theme`, `language`,
`split_chart`, `transparent_background`, `show_house_position_comparison`,
`show_cusp_position_comparison`, `show_degree_indicators`, `show_aspect_icons`,
`custom_title`

---

### Composite Charts

#### Composite Chart Data

**POST** `/api/v5/chart-data/composite`

Returns midpoint composite chart between two subjects.

**Request:**

```json
{
  "first_subject": { /* SubjectModel */ },
  "second_subject": { /* SubjectModel */ },
  "active_points": [...],
  "active_aspects": [...],
  "distribution_method": "weighted"
}
```

**Note:** This endpoint does **not** accept rendering parameters (`theme`,
`language`, `split_chart`, `transparent_background`,
`show_house_position_comparison`, `show_cusp_position_comparison`,
`show_degree_indicators`, `show_aspect_icons`, `custom_title`).

**Response:**

```json
{
  "status": "OK",
  "chart_data": {
    "chart_type": "Composite",
    "subject": { /* CompositeSubjectModel */ },
    "aspects": [ /* Internal composite aspects */ ],
    "element_distribution": {...},
    "quality_distribution": {...},
    "active_points": [...],
    "active_aspects": [...]
  }
}
```

#### Composite Chart with SVG

**POST** `/api/v5/chart/composite`

Returns composite data and rendered chart.

**Request:** Same as `/api/v5/chart-data/composite` plus `theme`, `language`,
`split_chart`, `transparent_background`, `show_house_position_comparison`,
`show_cusp_position_comparison`, `show_degree_indicators`, `show_aspect_icons`,
`custom_title`

---

### Planetary Returns

#### Solar Return Chart Data

**POST** `/api/v5/chart-data/solar-return`

Calculates solar return chart for a specific year.

**Request:**

```json
{
  "subject": { /* Natal SubjectModel */ },
  "year": 2024,
  "month": null,
  "iso_datetime": null,
  "wheel_type": "dual",
  "include_house_comparison": true,
  "return_location": {
    "city": "New York",
    "nation": "US",
    "longitude": -74.0060,
    "latitude": 40.7128,
    "timezone": "America/New_York"
  },
  "active_points": [...],
  "active_aspects": [...],
  "distribution_method": "weighted"
}
```

**Note:** This endpoint does **not** accept rendering parameters (`theme`,
`language`, `split_chart`, `transparent_background`,
`show_house_position_comparison`, `show_cusp_position_comparison`,
`show_degree_indicators`, `show_aspect_icons`, `custom_title`).

**Response:**

```json
{
  "status": "OK",
  "chart_data": {
    "chart_type": "DualReturnChart",
    "first_subject": { /* Natal subject */ },
    "second_subject": {
      "return_type": "Solar",
      /* Return chart data */
    },
    "aspects": [ /* Return-to-natal aspects */ ],
    "house_comparison": {...},
    "element_distribution": {...},
    "quality_distribution": {...}
  }
}
```

#### Solar Return Chart with SVG

**POST** `/api/v5/chart/solar-return`

Returns solar return data and rendered chart.

**Request:** Same as `/api/v5/chart-data/solar-return` plus `theme`, `language`,
`split_chart`, `transparent_background`, `show_house_position_comparison`,
`show_cusp_position_comparison`, `show_degree_indicators`, `show_aspect_icons`,
`custom_title`

**Response:** Adds `"return_type": "Solar"` and `"wheel_type": "dual"` or
`"single"`

#### Lunar Return Chart Data

**POST** `/api/v5/chart-data/lunar-return`

Calculates lunar return chart.

**Request:** Same structure as solar return

**Note:** This endpoint does **not** accept rendering parameters (`theme`,
`language`, `split_chart`, `transparent_background`,
`show_house_position_comparison`, `show_cusp_position_comparison`,
`show_degree_indicators`, `show_aspect_icons`, `custom_title`).

**Response:** Same structure with `"return_type": "Lunar"`

#### Lunar Return Chart with SVG

**POST** `/api/v5/chart/lunar-return`

Returns lunar return data and rendered chart.

**Request:** Same as `/api/v5/chart-data/lunar-return` plus `theme`, `language`,
`split_chart`, `transparent_background`, `show_house_position_comparison`,
`show_cusp_position_comparison`, `show_degree_indicators`, `show_aspect_icons`,
`custom_title`

#### Saturn Return Chart Data

**POST** `/api/v5/chart-data/saturn-return`

Calculates **Saturn return** chart data (next time transiting Saturn returns to
its natal ecliptic longitude).

**Request:** Same structure as `/api/v5/chart-data/solar-return`

**Response:** Same chart-data structure, plus top-level metadata:

```json
{
  "status": "OK",
  "chart_data": {/* DualReturnChart or SingleReturnChart */},
  "return_type": "Saturn",
  "wheel_type": "dual"
}
```

#### Jupiter Return Chart Data

**POST** `/api/v5/chart-data/jupiter-return`

Calculates **Jupiter return** chart data (next time transiting Jupiter returns
to its natal ecliptic longitude).

**Request:** Same structure as `/api/v5/chart-data/solar-return`

**Response:**

```json
{
  "status": "OK",
  "chart_data": {/* DualReturnChart or SingleReturnChart */},
  "return_type": "Jupiter",
  "wheel_type": "dual"
}
```

#### Lunar Node Return Chart Data (Mean North Node)

**POST** `/api/v5/chart-data/lunar-node-return`

Calculates **Mean North Lunar Node return** chart data (next time the **mean
node** returns to its natal ecliptic longitude).

**Request:** Same structure as `/api/v5/chart-data/solar-return`

**Response:**

```json
{
  "status": "OK",
  "chart_data": {/* DualReturnChart or SingleReturnChart */},
  "return_type": "MeanNode",
  "wheel_type": "dual"
}
```

---

### Lunar Phases

#### Lunar Phase Events (with optional Super Luna metrics)

**POST** `/api/v5/events/lunar-phases`

Computes exact **lunar quarter events** (`new_moon`, `first_quarter`, `full_moon`,
`last_quarter`) using:

1. A coarse Sun-Moon angle scan every 6 hours from `from_iso` to `horizon_days`
2. Crossing detection against target angles (0°/90°/180°/270°)
3. Refinement of crossing brackets to about 1-minute UTC precision

Optionally, the endpoint can enrich each event with:

- Moon-Earth distance at event time
- nearest perigee/apogee time and distance
- Super Luna classification for New/Full Moon

**Request (basic):**

```json
{
  "from_iso": "2026-03-01T00:00:00+00:00",
  "horizon_days": 40
}
```

**Request (with distance + Super Luna):**

```json
{
  "from_iso": "2026-03-01T00:00:00+00:00",
  "horizon_days": 365,
  "include_distance_metrics": true,
  "include_super_luna": true,
  "super_luna_definition": "nolle_90pct_cycle"
}
```

**Request (fixed threshold Super Luna):**

```json
{
  "from_iso": "2026-03-01T00:00:00+00:00",
  "horizon_days": 365,
  "include_super_luna": true,
  "super_luna_definition": "distance_threshold_km",
  "super_luna_distance_km_threshold": 360000
}
```

**Rules:**

- `from_iso` is optional (defaults to current UTC time)
- `horizon_days` is required, with max lookahead cap of 5 years (1826 days)
- `include_distance_metrics` is optional (default `false`)
- `include_super_luna` is optional (default `false`)
- `super_luna_definition` is optional:
  - `nolle_90pct_cycle` (default)
  - `distance_threshold_km`
- `super_luna_distance_km_threshold` is used only with `distance_threshold_km`

**Response (basic mode):**

```json
{
  "status": "OK",
  "from_iso": "2026-03-01T00:00:00+00:00",
  "horizon_days": 40,
  "events": [
    {
      "event": "full_moon",
      "at_utc": "2026-03-03T11:38:12.187500+00:00",
      "target_angle_deg": 180.0,
      "angle_deg": 180.00008579886356
    }
  ]
}
```

**Response (distance + Super Luna enabled):**

```json
{
  "status": "OK",
  "from_iso": "2026-03-01T00:00:00+00:00",
  "horizon_days": 40,
  "distance_frame": "geocentric",
  "distance_units": ["au", "km"],
  "super_luna_definition_applied": "nolle_90pct_cycle",
  "events": [
    {
      "event": "full_moon",
      "at_utc": "2026-03-03T11:38:12.187500+00:00",
      "target_angle_deg": 180.0,
      "angle_deg": 180.00008579886356,
      "moon_distance_au": 0.0025576090156967404,
      "moon_distance_km": 382612.52448331926,
      "nearest_perigee_utc": "2026-02-24T23:16:18.551524+00:00",
      "nearest_perigee_km": 370171.0227315845,
      "nearest_apogee_utc": "2026-03-10T13:42:23.411592+00:00",
      "nearest_apogee_km": 404344.5512508751,
      "delta_to_perigee_hours": 204.36517665999998,
      "anomalistic_closeness_pct": 63.593160288637876,
      "is_super_luna_candidate": true,
      "is_super_luna": false
    }
  ]
}
```

**Notes for backend integration:**

- In basic mode (default), only the original fields are returned.
- Distance/Super Luna fields are added per event only when requested.
- `is_super_luna_candidate` / `is_super_luna` apply to `new_moon` and `full_moon`
  events; quarter events are non-candidates.

---

### Retrogrades

#### Next Retrogrades (Per Planet)

**POST** `/api/v5/events/retrogrades`

Computes the **next retrograde window** for the requested planets using:

1. A coarse stream scan every 6 hours from `from_iso` to `horizon_days`
2. Motion by speed sign (`retrograde = speed < 0`)
3. Flip detection (`direct -> retro` start bracket, `retro -> direct` end bracket)
4. Refinement of flip brackets to about 1-minute UTC precision

**Request:**

```json
{
  "from_iso": "2026-01-15T12:00:00+00:00",
  "horizon_days": 180,
  "planets": ["Mercury", "venus", "MARS"],
  "include_ongoing": true
}
```

**Rules:**

- `from_iso` is optional (defaults to current UTC time)
- `horizon_days` is required, with max lookahead cap of 2 years (730 days)
- `planets` is required and validated against:
  `Mercury, Venus, Mars, Jupiter, Saturn, Uranus, Neptune, Pluto`
- Planet names are normalized case-insensitively and deduplicated

**`/next` semantics with `include_ongoing`:**

- If `include_ongoing=true` and a planet is already retrograde at `from_iso`,
  return that current window and mark:
  - `is_ongoing: true`
  - `started_before_from: true`
- If `include_ongoing=false`, return only strictly future windows
  (`next_start_utc > from_iso`)

**Response:**

```json
{
  "status": "OK",
  "from_iso": "2026-01-15T12:00:00+00:00",
  "horizon_days": 180,
  "include_ongoing": true,
  "retrogrades": [
    {
      "planet": "Mercury",
      "next_start_utc": "2026-04-21T03:59:32.812500+00:00",
      "next_end_utc": "2026-05-15T12:11:15.937500+00:00",
      "start_speed": -2.84e-05,
      "end_speed": 1.91e-05,
      "is_ongoing": false,
      "started_before_from": false
    }
  ]
}
```

---

### Ingress

#### Next Planetary Sign Ingress Events

**POST** `/api/v5/events/ingress`

Computes exact **zodiac sign ingress events** for selected planets using:

1. A coarse stream scan every 6 hours from `from_iso` to `horizon_days`
2. Sign-change detection (`sign_num` crossing between scan points)
3. Refinement of crossing brackets to about 1-minute UTC precision

**Request:**

```json
{
  "from_iso": "2026-01-15T12:00:00+00:00",
  "horizon_days": 30,
  "planets": ["Sun", "Moon", "Mercury"]
}
```

**Rules:**

- `from_iso` is optional (defaults to current UTC time)
- `horizon_days` is required, with max lookahead cap of 2 years (730 days)
- `planets` is optional. Defaults to:
  `Sun, Moon, Mercury, Venus, Mars, Jupiter, Saturn, Uranus, Neptune, Pluto`
- Planet names are normalized case-insensitively and deduplicated

**Response:**

```json
{
  "status": "OK",
  "from_iso": "2026-01-15T12:00:00+00:00",
  "horizon_days": 30,
  "planets": ["Sun", "Moon", "Mercury"],
  "events": [
    {
      "event": "sign_ingress",
      "planet": "Moon",
      "at_utc": "2026-01-16T03:21:00+00:00",
      "from_sign": "Can",
      "to_sign": "Leo"
    }
  ]
}
```

---

### Relationship Score

**POST** `/api/v5/compatibility-score`

Calculates Ciro Discepolo compatibility score between two subjects.

**Request:**

```json
{
  "first_subject": { /* SubjectModel */ },
  "second_subject": { /* SubjectModel */ },
  "active_points": [...],
  "active_aspects": [...]
}
```

**Response:**

```json
{
  "status": "OK",
  "score": 11,
  "score_description": "Very Important",
  "is_destiny_sign": true,
  "score_breakdown": [
    {
      "rule": "sun_moon_conjunction",
      "description": "Sun-Moon conjunction (high precision)",
      "points": 11,
      "details": "Sun-Moon conjunction (orbit: 1.34°)"
    }
  ],
  "aspects": [
    {
      "p1_name": "Sun",
      "p2_name": "Moon",
      "aspect": "conjunction",
      "orbit": 1.34
    }
  ],
  "chart_data": {
    "chart_type": "Synastry"
    /* Full synastry data */
  }
}
```

---

### Progressions

#### Progressed Moon Cycle (Secondary Progressions)

**POST** `/api/v5/chart-data/progressed-moon-cycle`

Computes **secondary progressed** Moon cycle data using a day-for-a-year
mapping:

- A progressed chart snapshot at `target_iso_datetime`
- Progressed lunation quarter phase (New / First Quarter / Full / Last Quarter)
- Next progressed Moon **sign ingress** and **house ingress** events occurring
  on the target timeline within the provided range

**Request:**

```json
{
  "subject": { /* SubjectModel */ },
  "target_iso_datetime": "2026-02-12T00:00:00+00:00",
  "range_end_iso_datetime": "2028-02-12T00:00:00+00:00",
  "step_days": 14,
  "active_points": ["Sun", "Moon", "Mercury", ...]
}
```

**Notes:**

- `target_iso_datetime` and `range_end_iso_datetime` must include a timezone
  offset (UTC recommended).
- `range_end_iso_datetime` must be later than `target_iso_datetime`.
- `active_points` is optional; **Sun and Moon are always enforced** for this
  endpoint.

**Response:**

```json
{
  "status": "OK",
  "progressed_moon_cycle": {
    "target_iso_datetime": "2026-02-12T00:00:00+00:00",
    "progressed_iso_datetime": "1999-03-01T00:00:00+00:00",
    "progressed_subject": {/* AstrologicalSubjectModel */},
    "progressed_lunation": {
      "angle_deg": 184.2,
      "phase_name": "Full Moon"
    },
    "next_ingresses": {
      "next_sign_ingress": {
        "at_target_iso_datetime": "2026-09-10T12:00:00+00:00",
        "at_progressed_iso_datetime": "1999-09-27T12:00:00+00:00",
        "sign": "Ge"
      },
      "next_house_ingress": {
        "at_target_iso_datetime": "2026-05-20T08:00:00+00:00",
        "at_progressed_iso_datetime": "1999-05-07T08:00:00+00:00",
        "house": "10"
      }
    }
  }
}
```

---

## AI Context Endpoints

The API provides 8 context endpoints that parallel the chart endpoints. Instead
of returning SVG charts, these endpoints return AI-optimized context strings
generated by Kerykeion's `to_context()` function, suitable for LLM consumption.

**Key Features:**

- Non-qualitative, factual astronomical positions
- Structured text format optimized for AI/LLM prompts
- Complete information including planetary positions, aspects, houses, and
  distributions
- Same request parameters as corresponding chart-data endpoints

### Subject Context Endpoints

#### Subject Context

**POST** `/api/v5/context/subject`

Returns astrological subject with AI-optimized context.

**Request:** Same as `/api/v5/subject`

**Response:**

```json
{
  "status": "OK",
  "subject_context": "Chart for \"Name\"...",
  "subject": {
    /* AstrologicalSubjectModel */
  }
}
```

#### Current Moment Context

**POST** `/api/v5/now/context`

Returns current UTC moment with AI context.

**Request:** Same as `/api/v5/now/subject`

**Response:**

```json
{
  "status": "OK",
  "subject_context": "Chart for \"Now\"...",
  "subject": {
    /* AstrologicalSubjectModel */
  }
}
```

### Chart Context Endpoints

All chart context endpoints return structured JSON data plus AI context string.

#### Natal Context

**POST** `/api/v5/context/birth-chart`

**Request:** Same as `/api/v5/chart-data/birth-chart`

**Response:**

```json
{
  "status": "OK",
  "context": "Natal Chart Analysis\n==================================================\n\nChart for \"Name\"...",
  "chart_data": {
    /* SingleChartDataModel */
  }
}
```

#### Synastry Context

**POST** `/api/v5/context/synastry`

**Request:** Same as `/api/v5/chart-data/synastry`

**Response:**

```json
{
  "status": "OK",
  "context": "Synastry Chart Analysis\n==================================================\n\nFirst Subject:...",
  "chart_data": {
    /* DualChartDataModel */
  }
}
```

#### Composite Context

**POST** `/api/v5/context/composite`

**Request:** Same as `/api/v5/chart-data/composite`

**Response:**

```json
{
  "status": "OK",
  "context": "Composite Chart Analysis...",
  "chart_data": {
    /* SingleChartDataModel */
  }
}
```

#### Transit Context

**POST** `/api/v5/context/transit`

**Request:** Same as `/api/v5/chart-data/transit`

**Response:**

```json
{
  "status": "OK",
  "context": "Transit Chart Analysis...",
  "chart_data": {
    /* DualChartDataModel */
  }
}
```

### Return Context Endpoints

#### Solar Return Context

**POST** `/api/v5/context/solar-return`

**Request:** Same as `/api/v5/chart-data/solar-return`

**Response:**

```json
{
  "status": "OK",
  "context": "DualReturnChart Chart Analysis...",
  "chart_data": {
    /* ChartDataModel */
  },
  "return_type": "Solar",
  "wheel_type": "dual"
}
```

#### Lunar Return Context

**POST** `/api/v5/context/lunar-return`

**Request:** Same as `/api/v5/chart-data/lunar-return`

**Response:**

```json
{
  "status": "OK",
  "context": "DualReturnChart Chart Analysis...",
  "chart_data": {
    /* ChartDataModel */
  },
  "return_type": "Lunar",
  "wheel_type": "dual"
}
```

### Integration with AI/LLMs

Context strings are designed for direct injection into AI prompts:

```python
import requests

response = requests.post(
    "http://localhost:8000/api/v5/context/birth-chart",
    headers={
        "X-Timestamp": "<unix_seconds>",
        "X-Signature": "<hex_or_base64_hmac>"
    },
    json={"subject": {...}}
)

context = response.json()["context"]

prompt = f"""
You are an expert astrologer. Analyze this natal chart:

{context}

Provide insights on career potential.
"""
```

**Benefits:**

- **No Visual Parsing**: LLMs get structured text instead of needing to parse
  SVG
- **Factual Data**: Non-qualitative, precise astronomical positions
- **Complete Information**: All planetary positions, aspects, houses, and
  distributions
- **Consistent Format**: Standardized output across all chart types

---

## Response Models

### Chart Types

- `"Natal"` - Single subject birth chart
- `"Synastry"` - Two-subject relationship comparison
- `"Transit"` - Current transits to natal chart
- `"Composite"` - Midpoint composite chart
- `"DualReturnChart"` - Return chart with natal comparison
- `"SingleReturnChart"` - Return chart alone

### Element Distribution Model

```json
{
  "fire": 5.0,
  "earth": 3.5,
  "air": 4.0,
  "water": 2.5,
  "fire_percentage": 33,
  "earth_percentage": 23,
  "air_percentage": 27,
  "water_percentage": 17
}
```

### Quality Distribution Model

```json
{
  "cardinal": 4.0,
  "fixed": 6.0,
  "mutable": 5.0,
  "cardinal_percentage": 27,
  "fixed_percentage": 40,
  "mutable_percentage": 33
}
```

### Aspect Model

```json
{
  "p1_name": "Sun",
  "p2_name": "Moon",
  "aspect": "conjunction",
  "orbit": 1.34,
  "aspect_degrees": 0,
  "aid": 1,
  "diff": 1.34,
  "p1": {
    /* Point details */
  },
  "p2": {
    /* Point details */
  }
}
```

---

## Distribution Methods

### Weighted (Default)

Uses traditional astrological weights:

- Sun, Moon, Ascendant: 2.0
- Personal planets (Mercury, Venus, Mars), Angles: 1.5
- Social planets (Jupiter, Saturn): 1.0
- Modern planets (Uranus, Neptune, Pluto): 0.5
- Asteroids and TNOs: 0.3-0.4

### Pure Count

Every active point counts as exactly 1.0.

### Custom Weights

Override specific weights:

```json
{
  "distribution_method": "weighted",
  "custom_distribution_weights": {
    "sun": 3.0,
    "moon": 2.5,
    "venus": 2.0,
    "__default__": 0.75
  }
}
```

---

## Error Responses

### 400 Bad Request

```json
{
  "status": "ERROR",
  "message": "Error description"
}
```

### 422 Validation Error

```json
{
  "detail": [
    {
      "loc": ["body", "subject", "year"],
      "msg": "field required",
      "type": "value_error.missing"
    }
  ]
}
```

### 500 Internal Server Error

```json
{
  "status": "ERROR",
  "message": "Internal server error"
}
```

---

## Rate Limits

Rate limits depend on your deployment and gateway configuration.

---

## Support

For issues or questions:

- GitHub: [Astrologer-API](https://github.com/g-battaglia/Astrologer-API)
- Email: kerykeion.astrology@gmail.com
- Website: [kerykeion.net](https://www.kerykeion.net/)
