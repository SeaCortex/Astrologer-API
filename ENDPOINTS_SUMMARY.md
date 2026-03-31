# Astrologer API v5 — Endpoints Summary (What Each Endpoint Returns)

This file is a **response-focused** companion to `ENDPOINTS.md`.

- It shows the **data returned** by each endpoint as compact example payloads.
- It uses `jsonc` blocks so we can add `// comments` explaining field meaning.

## Common response conventions

### Success vs error

Most endpoints return a success payload that includes:

```jsonc
{
  "status": "OK" // Success marker
}
```

On application errors, many endpoints return:

```jsonc
{
  "status": "ERROR", // Error marker
  "message": "Human message", // Error details
  "error_type": "Exception" // Exception class name
}
```

On HMAC auth failure, the middleware returns:

```jsonc
{
  "status": "KO", // Auth failure marker (middleware)
  "message": "Unauthorized - ... reason" // Why it was rejected
}
```

### `subject` vs `chart_data`

- **`subject`** is an `AstrologicalSubjectModel` (a single computed chart
  “snapshot”): planets/points, houses, angles, etc.
- **`chart_data`** is chart-level output:
  - `SingleChartDataModel` (one chart) or `DualChartDataModel` (comparison of
    two charts)
  - includes aspects, distributions, and comparison helpers depending on chart
    type.

### SVG fields

Only `/api/v5/chart/*` endpoints return SVG:

- `chart`: a single SVG string (default)
- `chart_wheel` + `chart_grid`: two separate SVG strings (when
  `split_chart=true`)

## Misc / Health

### GET `/api/v5/health`

Health check.

```jsonc
{
  "status": "OK" // API is healthy
}
```

## Current Moment

### POST `/api/v5/now/subject`

Returns an `AstrologicalSubjectModel` computed for **current UTC time at
Greenwich**.

```jsonc
{
  "status": "OK",
  "subject": {
    "name": "Now", // Request-provided label (defaults to "Now")

    // Computed point positions (subset shown)
    "planets": {
      "Sun": {
        "name": "Sun",
        "abs_pos": 320.12, // Absolute ecliptic longitude (0-360°)
        "sign": "Aq", // Sign abbreviation
        "position": 20.12, // Degrees within sign (0-30°)
        "house": "5" // House number as string
      }
      // ... other active points ...
    },

    // House cusp longitudes (subset shown)
    "houses": {
      "1": { "abs_pos": 123.4 },
      "2": { "abs_pos": 153.4 }
      // ... up to 12 ...
    },

    "active_points": ["Sun", "Moon" /* ... */] // Points actually computed
  }
}
```

### POST `/api/v5/now/chart`

Returns natal-style `chart_data` for “now” (current UTC time at Greenwich)
**plus SVG**.

```jsonc
{
  "status": "OK",
  "chart_data": {
    "chart_type": "Natal", // Discriminator for chart schema variant
    "subject": {/* AstrologicalSubjectModel */},
    "aspects": [
      {
        "p1_name": "Sun",
        "p2_name": "Moon",
        "aspect": "conjunction", // Aspect name
        "orbit": 3.25 // Distance from exact aspect in degrees
      }
    ],
    "element_distribution": {
      "fire": 5.0,
      "earth": 3.5,
      "air": 4.0,
      "water": 2.5,
      "fire_percentage": 33
    },
    "quality_distribution": {
      "cardinal": 4.0,
      "fixed": 6.0,
      "mutable": 5.0
    }
  },

  // SVG output (one of these shapes)
  "chart": "<svg>...</svg>" // Present when split_chart=false
  // "chart_wheel": "<svg>...</svg>", // Present when split_chart=true
  // "chart_grid": "<svg>...</svg>"   // Present when split_chart=true
}
```

## Subject Data

### POST `/api/v5/subject`

Builds and returns an `AstrologicalSubjectModel` from provided birth/event data
(no chart-level analysis).

```jsonc
{
  "status": "OK",
  "subject": {
    "name": "John Doe",
    "planets": {/* computed point positions */},
    "houses": {/* house cusps */},
    "active_points": ["Sun", "Moon" /* ... */]
  }
}
```

## Derived Data

### POST `/api/v5/derived/natal-profile`

Returns the computed `subject` plus a derived `derived_profile` object (Western
metrics).

```jsonc
{
  "status": "OK",
  "subject": {/* AstrologicalSubjectModel */},
  "derived_profile": {
    "chart_ruler": {
      "asc_sign": "Ar", // Ascendant sign abbreviation
      "ruler_point_name": "Mars", // Traditional ruler of asc_sign
      "ruler_point": null // Point details (only present if included in active_points)
    },
    "stelliums": {
      "min_count": 3, // Minimum number of points to qualify as a stellium
      "by_sign": [{ "sign": "Ar", "points": ["Sun", "Mercury", "Venus"] }],
      "by_house": [{ "house": "1", "points": ["Sun", "Mercury", "Venus"] }]
    },
    "hemispheres": {
      "above_below_horizon": {
        "above_count": 4, // Houses 7-12
        "below_count": 6, // Houses 1-6
        "above_pct": 40.0,
        "below_pct": 60.0,
        "counted_points": ["Sun", "Moon" /* ... */]
      },
      "east_west": {
        "east_count": 7,
        "west_count": 3,
        "east_pct": 70.0,
        "west_pct": 30.0,
        "counted_points": ["Sun", "Moon" /* ... */]
      }
    },
    "lunar_mansion": {
      "system": "tropical_28_equal", // Western 28-equal tropical system
      "index": 12, // 1..28
      "start_abs_deg": 141.4286,
      "end_abs_deg": 154.2857,
      "moon_abs_pos": 149.12
    }
  }
}
```

## Natal Charts

### POST `/api/v5/chart-data/birth-chart`

Natal chart **data only** (no SVG).

```jsonc
{
  "status": "OK",
  "chart_data": {
    "chart_type": "Natal",
    "subject": {/* AstrologicalSubjectModel */},
    "aspects": [/* within-chart aspects */],
    "element_distribution": {/* element counts + percentages */},
    "quality_distribution": {/* quality counts + percentages */},
    "hemispheres_distribution": {/* hemisphere distribution */},
    "active_points": ["Sun", "Moon" /* ... */],
    "active_aspects": [{ "name": "conjunction", "orb": 10 } /* ... */]
  }
}
```

### POST `/api/v5/chart/birth-chart`

Natal chart data **plus SVG**.

```jsonc
{
  "status": "OK",
  "chart_data": {/* same shape as /chart-data/birth-chart */},
  "chart": "<svg>...</svg>"
}
```

## Synastry Charts

### POST `/api/v5/chart-data/synastry`

Synastry (two subjects compared), **data only** (no SVG).

```jsonc
{
  "status": "OK",
  "chart_data": {
    "chart_type": "Synastry",
    "first_subject": {/* Person A subject (inner wheel) */},
    "second_subject": {/* Person B subject (outer wheel) */},
    "aspects": [/* inter-aspects between A and B */],
    "house_comparison": {/* optional overlays (if enabled) */},
    "relationship_score": {/* optional (if enabled) */}
  }
}
```

### POST `/api/v5/chart/synastry`

Synastry data **plus SVG**.

```jsonc
{
  "status": "OK",
  "chart_data": {/* same shape as /chart-data/synastry */},
  "chart": "<svg>...</svg>"
}
```

## Transit Charts

### POST `/api/v5/chart-data/transit`

Transits-to-natal (natal vs transit moment), **data only** (no SVG).

```jsonc
{
  "status": "OK",
  "chart_data": {
    "chart_type": "Transit",
    "first_subject": {/* Natal subject */},
    "second_subject": {/* Transit moment subject */},
    "aspects": [/* transit-to-natal aspects */],
    "house_comparison": {/* optional overlays (if enabled) */}
  }
}
```

### POST `/api/v5/chart/transit`

Transit data **plus SVG**.

```jsonc
{
  "status": "OK",
  "chart_data": {/* same shape as /chart-data/transit */},
  "chart": "<svg>...</svg>"
}
```

## Composite Charts

### POST `/api/v5/chart-data/composite`

Midpoint composite chart, **data only** (no SVG).

```jsonc
{
  "status": "OK",
  "chart_data": {
    "chart_type": "Composite",
    "subject": {/* Composite subject chart */},
    "aspects": [/* within-composite aspects */],
    "element_distribution": {/* ... */},
    "quality_distribution": {/* ... */}
  }
}
```

### POST `/api/v5/chart/composite`

Composite data **plus SVG**.

```jsonc
{
  "status": "OK",
  "chart_data": {/* same shape as /chart-data/composite */},
  "chart": "<svg>...</svg>"
}
```

## Planetary Returns

### POST `/api/v5/chart-data/solar-return`

Solar return **data only** (no SVG).

```jsonc
{
  "status": "OK",
  "chart_data": {
    "chart_type": "DualReturnChart", // or "SingleReturnChart" depending on wheel_type

    // Dual wheel: natal + return
    "first_subject": {/* Natal subject */},
    "second_subject": {
      "return_type": "Solar", // Return kind (inside the return subject)
      "planets": {/* ... */},
      "houses": {/* ... */}
    },
    "aspects": [/* return-to-natal aspects */],
    "house_comparison": {/* optional */}
    // Single wheel variant includes just:
    // "subject": { "return_type": "Solar", ... }
  }
}
```

### POST `/api/v5/chart/solar-return`

Solar return **plus SVG**, with top-level metadata:

```jsonc
{
  "status": "OK",
  "chart_data": {/* same as /chart-data/solar-return */},
  "chart": "<svg>...</svg>",
  "return_type": "Solar", // Top-level convenience field
  "wheel_type": "dual" // "dual" (natal+return) or "single" (return only)
}
```

### POST `/api/v5/chart-data/lunar-return`

Lunar return **data only** (no SVG).

```jsonc
{
  "status": "OK",
  "chart_data": {
    "chart_type": "DualReturnChart",
    "first_subject": {/* Natal */},
    "second_subject": { "return_type": "Lunar" /* ... */ }
  }
}
```

### POST `/api/v5/chart/lunar-return`

Lunar return **plus SVG**, with top-level metadata:

```jsonc
{
  "status": "OK",
  "chart_data": {/* same as /chart-data/lunar-return */},
  "chart": "<svg>...</svg>",
  "return_type": "Lunar",
  "wheel_type": "dual"
}
```

### POST `/api/v5/chart-data/saturn-return`

Saturn return **data only** (no SVG), with explicit top-level metadata:

```jsonc
{
  "status": "OK",
  "chart_data": {/* DualReturnChart or SingleReturnChart */},
  "return_type": "Saturn", // Endpoint return kind
  "wheel_type": "dual"
}
```

### POST `/api/v5/chart-data/jupiter-return`

```jsonc
{
  "status": "OK",
  "chart_data": {/* DualReturnChart or SingleReturnChart */},
  "return_type": "Jupiter",
  "wheel_type": "dual"
}
```

### POST `/api/v5/chart-data/lunar-node-return`

Mean North Lunar Node return (Mean Node) **data only**:

```jsonc
{
  "status": "OK",
  "chart_data": {/* DualReturnChart or SingleReturnChart */},
  "return_type": "MeanNode", // Mean North Node return
  "wheel_type": "dual"
}
```

## Relationship Score

### POST `/api/v5/compatibility-score`

Score plus supporting details, and includes the underlying synastry chart data.

```jsonc
{
  "status": "OK",
  "score": 11.0,
  "score_description": "Very Important",
  "is_destiny_sign": true,
  "aspects": [/* aspects used in scoring */],
  "score_breakdown": [/* rule-by-rule scoring detail */],
  "chart_data": {/* DualChartDataModel (Synastry) */}
}
```

## Retrogrades

### POST `/api/v5/retrogrades/next`

Next retrograde window per requested planet (stream scan + refined station times).

```jsonc
{
  "status": "OK",
  "from_iso": "2026-01-15T12:00:00+00:00",
  "horizon_days": 180,
  "include_ongoing": true,
  "retrogrades": [
    {
      "planet": "Mercury",
      "next_start_utc": "2026-04-21T03:59:32.812500+00:00", // null if started before from_iso
      "next_end_utc": "2026-05-15T12:11:15.937500+00:00", // null if end not found in horizon
      "start_speed": -0.0000284,
      "end_speed": 0.0000191,
      "is_ongoing": false,
      "started_before_from": false
    }
  ]
}
```

Rules:

- `planets` required (Mercury, Venus, Mars, Jupiter, Saturn, Uranus, Neptune, Pluto), case-insensitive, deduplicated.
- `from_iso` optional (defaults to current UTC).
- `horizon_days` required with cap 730 days (2 years).
- If `include_ongoing=true` and already retrograde at `from_iso`, returns current window with
  `is_ongoing=true`, `started_before_from=true`.
- If `include_ongoing=false`, returns only strictly future windows (`next_start_utc > from_iso`).

## Progressions

### POST `/api/v5/chart-data/progressed-moon-cycle`

Secondary progressed Moon cycle data (no SVG).

```jsonc
{
  "status": "OK",
  "progressed_moon_cycle": {
    "target_iso_datetime": "2026-02-12T00:00:00+00:00", // Target real-world timeline datetime
    "progressed_iso_datetime": "1999-03-01T00:00:00+00:00", // Progressed datetime (day-for-year mapping)
    "progressed_subject": {/* AstrologicalSubjectModel for progressed chart */},
    "progressed_lunation": {
      "angle_deg": 184.2, // Progressed Sun–Moon separation
      "phase_name": "Full Moon" // Quarter bucket (New/First/Full/Last)
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

## AI Context Endpoints

These mirror chart/subject endpoints but also include AI-optimized text fields.

### POST `/api/v5/context/subject`

```jsonc
{
  "status": "OK",
  "subject_context": "Chart for ...", // AI-optimized context string
  "subject": {/* AstrologicalSubjectModel */}
}
```

### POST `/api/v5/now/context`

```jsonc
{
  "status": "OK",
  "subject_context": "Chart for ...", // Context for current UTC time at Greenwich
  "subject": {/* AstrologicalSubjectModel */}
}
```

### POST `/api/v5/context/birth-chart`

```jsonc
{
  "status": "OK",
  "context": "Natal Chart Analysis...",
  "chart_data": {/* SingleChartDataModel (Natal) */}
}
```

### POST `/api/v5/context/synastry`

```jsonc
{
  "status": "OK",
  "context": "Synastry Chart Analysis...",
  "chart_data": {/* DualChartDataModel (Synastry) */}
}
```

### POST `/api/v5/context/composite`

```jsonc
{
  "status": "OK",
  "context": "Composite Chart Analysis...",
  "chart_data": {/* SingleChartDataModel (Composite) */}
}
```

### POST `/api/v5/context/transit`

```jsonc
{
  "status": "OK",
  "context": "Transit Chart Analysis...",
  "chart_data": {/* DualChartDataModel (Transit) */}
}
```

### POST `/api/v5/context/solar-return`

```jsonc
{
  "status": "OK",
  "context": "DualReturnChart Chart Analysis...",
  "chart_data": {/* DualReturnChart or SingleReturnChart */},
  "return_type": "Solar",
  "wheel_type": "dual"
}
```

### POST `/api/v5/context/lunar-return`

```jsonc
{
  "status": "OK",
  "context": "DualReturnChart Chart Analysis...",
  "chart_data": {/* DualReturnChart or SingleReturnChart */},
  "return_type": "Lunar",
  "wheel_type": "dual"
}
```
