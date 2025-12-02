# Astrologer API

Astrologer API lets you add **professional-grade astrology features** to any app, fast!  
It delivers both **plug-and-play SVG charts** and **rich astrological data** for natal, synastry, transits, composites, and returns.

-   NASA-grade astronomical accuracy
-   Production-ready JSON + beautiful SVGs
-   Used in astrology apps, compatibility/dating systems, dashboards and SaaS tools

Birth chart example (dark theme):
![Birth chart example](https://raw.githubusercontent.com/g-battaglia/kerykeion/refs/heads/main/tests/charts/svg/John%20Lennon%20-%20Dark%20Theme%20-%20Natal%20Chart.svg)

👉 Ready to use it? [SUBSCRIBE NOW](https://rapidapi.com/gbattaglia/api/astrologer/pricing) Subscribe on RapidAPI.

> Looking fort the old V4 docs? See [V4 Docs](https://github.com/g-battaglia/Astrologer-API/tree/v4).

## Quick start

Every request must include your RapidAPI key.

Headers:

```javascript
{
    'X-RapidAPI-Host': 'astrologer.p.rapidapi.com',
    'X-RapidAPI-Key': 'YOUR_API_KEY',
    'Content-Type': 'application/json'
}
```

Minimal birth chart request (SVG + data):

```bash
curl -X POST 'https://astrologer.p.rapidapi.com/api/v5/chart/birth-chart' \
    -H 'Content-Type: application/json' \
    -H 'X-RapidAPI-Host: astrologer.p.rapidapi.com' \
    -H 'X-RapidAPI-Key: YOUR_API_KEY' \
    -d '{
        "subject": {
            "name": "John Doe",
            "year": 1980,
            "month": 12,
            "day": 12,
            "hour": 12,
            "minute": 12,
            "longitude": 0,
            "latitude": 51.4825766,
            "timezone": "Europe/London"
        },
        "theme": "dark"
    }'
```

Response shape:

```json
{
    "status": "OK",
    "chart": "<svg>...</svg>",
    "chart_data": {
        /* aspects, houses, distributions, subjects */
    }
}
```

Prefer separate SVGs? Use "split_chart": true. You'll receive chart_wheel and chart_grid instead of chart. See the split example below.

## Endpoints

### `/api/v5/chart/birth-chart` (POST)

Returns a birth chart as an SVG along with full natal data.

### `/api/v5/chart-data/birth-chart` (POST)

Returns birth chart data only, without SVG.

### `/api/v5/chart/synastry` (POST)

Returns a synastry chart as an SVG along with combined data for both subjects.

### `/api/v5/chart-data/synastry` (POST)

Returns synastry data only, without SVG.

### `/api/v5/chart/transit` (POST)

Returns a transit chart as an SVG, including both natal and current (moment) data.

### `/api/v5/chart-data/transit` (POST)

Returns transit data only, without SVG.

### `/api/v5/chart/composite` (POST)

Returns a composite chart as an SVG along with midpoint data.

### `/api/v5/chart-data/composite` (POST)

Returns composite data only, without SVG.

### `/api/v5/chart/solar-return` (POST)

Returns a solar return chart as an SVG (dual or single wheel) along with related data.

### `/api/v5/chart-data/solar-return` (POST)

Returns solar return data only, without SVG.

### `/api/v5/chart/lunar-return` (POST)

Returns a lunar return chart as an SVG (dual or single wheel) along with related data.

### `/api/v5/chart-data/lunar-return` (POST)

Returns lunar return data only, without SVG.

### `/api/v5/compatibility-score` (POST)

Calculates the Ciro Discepolo compatibility score and provides a synastry summary.

### `/api/v5/subject` (POST)

Returns a normalized subject object only, without aspects or SVG.

### `/api/v5/now/subject` (GET)

Returns the subject for the current UTC time (Greenwich).

### `/api/v5/now/chart` (GET)

Returns the current time chart as an SVG along with data.

### Context Endpoints (AI/LLM Integration)

The API provides AI-optimized context endpoints that return structured textual descriptions instead of SVG charts. These are designed for LLM integration and AI applications:

-   `/api/v5/context/subject` (POST) - Subject data with AI context
-   `/api/v5/context/birth-chart` (POST) - Natal chart data with AI context
-   `/api/v5/context/synastry` (POST) - Synastry data with AI context
-   `/api/v5/context/composite` (POST) - Composite data with AI context
-   `/api/v5/context/transit` (POST) - Transit data with AI context
-   `/api/v5/context/solar-return` (POST) - Solar return data with AI context
-   `/api/v5/context/lunar-return` (POST) - Lunar return data with AI context
-   `/api/v5/now/context` (POST) - Current moment with AI context

These endpoints accept the same parameters as their corresponding chart-data endpoints but return `context` (AI-optimized text) instead of SVG charts.

Full reference: ENDPOINTS.md • Swagger • Redoc • OpenAPI (links below)

## Copy‑paste examples

### 1) Natal chart (SVG + data)

```bash
curl -X POST 'https://astrologer.p.rapidapi.com/api/v5/chart/birth-chart' \
    -H 'Content-Type: application/json' \
    -H 'X-RapidAPI-Host: astrologer.p.rapidapi.com' \
    -H 'X-RapidAPI-Key: YOUR_API_KEY' \
    -d '{
        "subject": { "name": "Ada", "year": 1990, "month": 5, "day": 1, "hour": 10, "minute": 0, "longitude": 12.4964, "latitude": 41.9028, "timezone": "Europe/Rome" },
        "theme": "light",
        "language": "EN"
    }'
```

Two SVGs (wheel + grid) with split_chart:

-   When you add "split_chart": true, the response does not include the single "chart" key.
-   Instead you get two SVGs:
    -   chart_wheel: the zodiac wheel (signs, houses, degrees, glyphs)
    -   chart_grid: the aspect grid/table and legend
-   Useful when you need separate positioning, animation, or different sizes for wheel and grid.
-   Works with all /charts/\* endpoints and can be combined with transparent_background.

Request:

```bash
curl -X POST 'https://astrologer.p.rapidapi.com/api/v5/chart/birth-chart' \
    -H 'Content-Type: application/json' \
    -H 'X-RapidAPI-Host: astrologer.p.rapidapi.com' \
    -H 'X-RapidAPI-Key: YOUR_API_KEY' \
    -d '{
        "subject": { "name": "Ada", "year": 1990, "month": 5, "day": 1, "hour": 10, "minute": 0, "longitude": 12.4964, "latitude": 41.9028, "timezone": "Europe/Rome" },
        "split_chart": true
    }'
```

Response (shape):

```json
{
    "status": "OK",
    "chart_wheel": "<svg>...</svg>",
    "chart_grid": "<svg>...</svg>",
    "chart_data": {
        /* ... */
    }
}
```

Make the SVG background transparent:

```bash
... -d '{ "subject": { /* as above */ }, "transparent_background": true }'
```

Data‑only variant:

```bash
curl -X POST 'https://astrologer.p.rapidapi.com/api/v5/chart-data/birth-chart' \
    -H 'Content-Type: application/json' \
    -H 'X-RapidAPI-Host: astrologer.p.rapidapi.com' \
    -H 'X-RapidAPI-Key: YOUR_API_KEY' \
    -d '{ "subject": { "name": "Ada", "year": 1990, "month": 5, "day": 1, "hour": 10, "minute": 0, "longitude": 12.4964, "latitude": 41.9028, "timezone": "Europe/Rome" } }'
```

### 2) Synastry chart

```bash
curl -X POST 'https://astrologer.p.rapidapi.com/api/v5/chart/synastry' \
    -H 'Content-Type: application/json' \
    -H 'X-RapidAPI-Host: astrologer.p.rapidapi.com' \
    -H 'X-RapidAPI-Key: YOUR_API_KEY' \
    -d '{
        "first_subject": { "name": "Alice", "year": 1990, "month": 7, "day": 5, "hour": 9, "minute": 30, "longitude": -0.1278, "latitude": 51.5074, "timezone": "Europe/London" },
        "second_subject": { "name": "Bob", "year": 1988, "month": 1, "day": 20, "hour": 18, "minute": 15, "longitude": 2.3522, "latitude": 48.8566, "timezone": "Europe/Paris" },
        "theme": "dark"
    }'
```

Compatibility score only (fast):

```bash
curl -X POST 'https://astrologer.p.rapidapi.com/api/v5/compatibility-score' \
    -H 'Content-Type: application/json' \
    -H 'X-RapidAPI-Host: astrologer.p.rapidapi.com' \
    -H 'X-RapidAPI-Key: YOUR_API_KEY' \
    -d '{
        "first_subject": { /* as above */ },
        "second_subject": { /* as above */ }
    }'
```

### 3) Transits (now or custom moment)

Current time (simple GET):

```bash
curl 'https://astrologer.p.rapidapi.com/api/v5/now/chart' \
    -H 'X-RapidAPI-Host: astrologer.p.rapidapi.com' \
    -H 'X-RapidAPI-Key: YOUR_API_KEY'
```

Transit for a natal subject at a chosen moment:

```bash
curl -X POST 'https://astrologer.p.rapidapi.com/api/v5/chart/transit' \
    -H 'Content-Type: application/json' \
    -H 'X-RapidAPI-Host: astrologer.p.rapidapi.com' \
    -H 'X-RapidAPI-Key: YOUR_API_KEY' \
    -d '{
        "first_subject": { /* natal subject */ },
        "transit_subject": { "year": 2025, "month": 1, "day": 1, "hour": 0, "minute": 0, "longitude": 0, "latitude": 51.48, "timezone": "Europe/London" }
    }'
```

### 4) Solar return

```bash
curl -X POST 'https://astrologer.p.rapidapi.com/api/v5/chart/solar-return' \
    -H 'Content-Type: application/json' \
    -H 'X-RapidAPI-Host: astrologer.p.rapidapi.com' \
    -H 'X-RapidAPI-Key: YOUR_API_KEY' \
    -d '{
        "subject": { /* natal */ },
        "year": 2025,
        "wheel_type": "dual",
        "return_location": { "longitude": -74.0060, "latitude": 40.7128, "timezone": "America/New_York" }
    }'
```

## Options at a glance

There are two kinds of options:

-   Computation options (work everywhere, including /chart-data/\*):

    -   active_points, active_aspects
    -   distribution_method: "weighted" (default) or "pure_count"
    -   custom_distribution_weights: override weights selectively

-   Rendering options (only for /charts/\* endpoints):
    -   theme: light, dark, dark-high-contrast, classic
    -   language: EN, FR, PT, ES, TR, RU, IT, CN, DE, HI
    -   split_chart: true to receive wheel and grid separately
    -   transparent_background: true for transparent SVG background
    -   show_house_position_comparison: false hides the comparison table and widens the SVG layout
    -   custom_title: short (≤40 chars) override for the title printed on the chart

Quick example with custom weights:

```json
{
    "distribution_method": "weighted",
    "custom_distribution_weights": {
        "sun": 2.0,
        "moon": 2.0,
        "ascendant": 2.0,
        "medium_coeli": 1.5,
        "mercury": 1.5,
        "venus": 1.5,
        "mars": 1.5,
        "jupiter": 1.0,
        "saturn": 1.0
    }
}
```

For full lists of points/aspects/themes and defaults, see the docs below.

## Languages

Localize chart labels and texts by setting the language parameter (default: EN).

Supported codes:

-   EN (English)
-   FR (French)
-   PT (Portuguese)
-   ES (Spanish)
-   TR (Turkish)
-   RU (Russian)
-   IT (Italian)
-   CN (Chinese)
-   DE (German)
-   HI (Hindi)

Example:

```json
{
    "subject": {
        /* ... */
    },
    "language": "RU"
}
```

## Transparent background

Render charts without a background fill so you can overlay them on any design. Works with any theme and across all /charts/\* endpoints. Can be combined with split_chart.

Example:

```json
{
    "subject": {
        /* ... */
    },
    "theme": "dark",
    "transparent_background": true
}
```

## Hide the house comparison table

On single-wheel charts the default layout includes the house comparison table. Set `show_house_position_comparison` to `false` to hide that panel and allow the SVG to use the extra width.

```json
{
    "subject": {
        /* ... */
    },
    "show_house_position_comparison": false
}
```

## Custom chart titles

Provide a short (`<= 40` chars) `custom_title` to override the text rendered above the chart for that single request. Whitespace is trimmed and empty strings are ignored.

```json
{
    "subject": {
        /* ... */
    },
    "custom_title": "Alice & Bob (Q1 2025)"
}
```

## Zodiac types (Tropical vs Sidereal)

Choose the zodiac in the subject object:

-   zodiac_type: "Tropic" (default) or "Sidereal"
-   If "Sidereal", also set sidereal_mode (ayanamsha)

Supported sidereal_mode values include:

-   FAGAN_BRADLEY, LAHIRI, DELUCE, RAMAN, USHASHASHI, KRISHNAMURTI, DJWHAL_KHUL, YUKTESHWAR, JN_BHASIN,
-   BABYL_KUGLER1, BABYL_KUGLER2, BABYL_KUGLER3, BABYL_HUBER, BABYL_ETPSC,
-   ALDEBARAN_15TAU, HIPPARCHOS, SASSANIAN, J2000, J1900, B1950

Example (Sidereal):

```json
{
    "subject": {
        "name": "John Doe",
        "year": 1980,
        "month": 12,
        "day": 12,
        "hour": 12,
        "minute": 12,
        "longitude": 0,
        "latitude": 51.4826,
        "timezone": "Europe/London",
        "zodiac_type": "Sidereal",
        "sidereal_mode": "FAGAN_BRADLEY"
    }
}
```

## House systems

Select the house system via subject.house_system using one of the codes:

-   A: Equal
-   B: Alcabitius
-   C: Campanus
-   D: Equal (MC)
-   F: Carter poli-equ.
-   H: Horizon/Azimut
-   I: Sunshine
-   i: Sunshine/Alt.
-   K: Koch
-   L: Pullen SD
-   M: Morinus
-   N: Equal/1=Aries
-   O: Porphyry
-   P: Placidus (common default)
-   Q: Pullen SR
-   R: Regiomontanus
-   S: Sripati
-   T: Polich/Page (Koch/Topocentric variant)
-   U: Krusinski-Pisa-Goelzer
-   V: Equal/Vehlow
-   W: Equal/Whole Sign
-   X: Axial rotation/Meridian houses
-   Y: APC houses

Example:

```json
{
    "subject": {
        "name": "John Doe",
        "year": 1980,
        "month": 12,
        "day": 12,
        "hour": 12,
        "minute": 12,
        "longitude": 0,
        "latitude": 51.4826,
        "timezone": "Europe/London",
        "zodiac_type": "Tropic",
        "house_system": "P"
    }
}
```

## Automatic coordinates (optional)

Skip longitude/latitude/timezone by providing a Geonames username. When `geonames_username` is present in `subject`, coordinates and timezone are looked up automatically.

```json
{
    "subject": {
        "city": "Jamaica, New York",
        "nation": "US",
        "year": 1980,
        "month": 12,
        "day": 12,
        "hour": 12,
        "minute": 12,
        "geonames_username": "YOUR_GEONAMES_USERNAME"
    }
}
```

Tip: For best accuracy, send actual coordinates when you can. Geonames is free up to ~10k requests/day.

## Troubleshooting

-   422 Unprocessable Entity: Double‑check required fields (subject.year/month/day/hour/minute and location). `/chart-data/*` endpoints reject rendering options such as theme, language, split_chart, transparent_background, show_house_position_comparison, custom_title.
-   Timezone errors: Use a valid tz database name (e.g. "Europe/Rome").
-   Empty SVG or missing wheel/grid: Use `/chart/*` endpoints for rendering. `/chart-data/*` never return SVG.

## Documentation

-   Swagger (interactive): https://www.kerykeion.net/astrologer-api-swagger/
-   Redoc (reference): https://www.kerykeion.net/astrologer-api-redoc/
-   OpenAPI JSON: https://raw.githubusercontent.com/g-battaglia/Astrologer-API/master/openapi.json
-   Project docs: site-docs/README.md

## Subscription and support

Subscribe: https://rapidapi.com/gbattaglia/api/astrologer/pricing

If you need higher quotas or a custom plan beyond the default tiers, reach out via [kerykeion.astrology@gmail.com](mailto:kerykeion.astrology@gmail.com) to discuss tailored options.

Licensing note: Astrologer API is open source (AGPLv3). Using the hosted API via RapidAPI is allowed in any app, including closed‑source. If you disclose providers, you may use: “Astrological data and charts are generated using Astrologer API.”
