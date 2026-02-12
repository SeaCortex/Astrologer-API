# Chart Data Endpoints Explained

This document explains what each chart data endpoint returns, written for those
new to astrology.

## Core Concepts

**Planets**: The Sun, Moon, Mercury, Venus, Mars, Jupiter, Saturn, Uranus,
Neptune, Pluto, and other celestial points (like the Ascendant, which is the
eastern horizon at birth).

**Signs**: The 12 zodiac signs (Aries, Taurus, Gemini, Cancer, Leo, Virgo,
Libra, Scorpio, Sagittarius, Capricorn, Aquarius, Pisces). Each planet is "in" a
sign.

**Houses**: 12 divisions of the sky (1st through 12th house) representing
different life areas. Each house has a "cusp" (starting point).

**Aspects**: Angular relationships between planets (e.g., Conjunction = 0°,
Trine = 120°, Square = 90°). Aspects indicate how planets interact.

**Elements**: Fire, Earth, Air, Water - each sign belongs to one element.

**Qualities**: Cardinal, Fixed, Mutable - each sign belongs to one quality.

---

## 1. `/api/v5/subject` - Basic Subject Data

**What it does**: Calculates the basic planetary positions for a single person
at a specific time and location.

**Returns**:

- `subject`: A single person's astrological data
  - `planets`: Where each planet was positioned (sign, degree, house)
  - `houses`: The 12 house cusps (starting points)
  - `lunar_phase`: Moon phase (New Moon, First Quarter, Full Moon, etc.)
  - `active_points`: List of planets/points included in the calculation

**Use case**: Get raw planetary positions without any relationship analysis or
chart comparisons.

**Example**: "Where was the Sun when John was born?" → Sun in Scorpio, 2.5°,
12th House.

---

## 2. `/api/v5/chart-data/birth-chart` - Natal Chart (Birth Chart)

**What it does**: A complete snapshot of the sky at the moment of birth. This is
the foundation chart used for all other analyses.

**Returns**:

- `chart_data`:
  - `subject`: The person's birth data
  - `planets`: All planetary positions (sign, degree, house for each planet)
  - `houses`: The 12 house cusps
  - `aspects`: **Aspects between planets in the same chart** (e.g., "Sun
    conjunct Moon", "Venus square Mars")
  - `element_distribution`: How many planets fall in Fire/Earth/Air/Water signs
    (with percentages)
  - `quality_distribution`: How many planets fall in Cardinal/Fixed/Mutable
    signs (with percentages)
  - `hemispheres_distribution`: Distribution across chart hemispheres
    (top/bottom, left/right)

**Use case**: Understand a person's core personality traits, strengths,
challenges, and life themes based on their birth chart.

**Example**: "What's John's personality like?" → Sun in Scorpio (intense,
private), Moon in Cancer (emotional, nurturing), lots of Water element
(emotional depth), many aspects showing internal tension.

---

## 3. `/api/v5/chart-data/synastry` - Relationship Comparison

**What it does**: Compares two people's birth charts to see how they interact.
Shows where Person B's planets fall in relation to Person A's chart.

**Returns**:

- `chart_data`:
  - `first_subject`: Person A's complete birth chart
  - `second_subject`: Person B's complete birth chart
  - `aspects`: **Inter-aspects** - aspects between Person A's planets and Person
    B's planets (e.g., "Person A's Sun trines Person B's Moon")
  - `house_comparison` (optional): Where Person B's planets fall in Person A's
    houses (e.g., "Person B's Sun is in Person A's 7th house" = relationship
    focus)
  - `relationship_score` (optional): Compatibility score with breakdown
  - `element_distribution` / `quality_distribution`: Combined analysis

**Use case**: Analyze romantic compatibility, friendship dynamics, or any
relationship between two people.

**Example**: "Are Alice and Bob compatible?" → Alice's Sun trines Bob's Moon
(emotional harmony), Bob's Venus is in Alice's 7th house (strong romantic
attraction), high compatibility score.

---

## 4. `/api/v5/compatibility-score` - Quick Compatibility Score

**What it does**: A specialized endpoint that calculates a numerical
compatibility score between two people using the Ciro Discepolo method. Faster
than full synastry if you only need the score.

**Returns**:

- `score`: Numerical score (typically -20 to +20, higher = more compatible)
- `score_description`: Text description (e.g., "Very high compatibility")
- `is_destiny_sign`: Boolean indicating if they share a special sign connection
- `aspects`: List of inter-aspects that contributed to the score
- `score_breakdown`: Detailed list of which rules/patterns contributed points
  (e.g., "Sun-Moon conjunction: +11 points")
- `chart_data`: Full synastry data (same as `/chart-data/synastry`)

**Use case**: Quick compatibility check for dating apps, relationship analysis
tools.

**Example**: Score of 15.5 = "Very high compatibility" with breakdown showing
which planetary connections created the score.

---

## 5. `/api/v5/chart-data/composite` - Relationship as a Third Entity

**What it does**: Creates a single "composite" chart representing the
relationship itself. Calculates midpoints between the two people's planets
(e.g., if Person A's Sun is at 10° and Person B's Sun is at 20°, the composite
Sun is at 15°).

**Returns**:

- `chart_data`:
  - `subject`: The composite chart (a single chart, not two)
  - `planets`: Midpoint positions for each planet
  - `houses`: Houses calculated for the composite
  - `aspects`: Aspects within the composite chart itself
  - `element_distribution` / `quality_distribution`: Analysis of the composite

**Use case**: Understand the relationship as its own entity - what the
relationship is like, its purpose, and how it functions.

**Example**: Composite Sun in Aquarius = the relationship is about friendship,
innovation, and independence. Composite Moon in Cancer = the relationship
provides emotional security and nurturing.

---

## 6. `/api/v5/chart-data/transit` - Current Influences on Birth Chart

**What it does**: Compares a person's birth chart (natal) with the current
positions of planets in the sky (transits). Shows what planetary influences are
affecting them right now or at a specific future date.

**Returns**:

- `chart_data`:
  - `first_subject`: The natal (birth) chart
  - `second_subject`: The transit chart (current/future sky)
  - `aspects`: **Transit-to-natal aspects** - how current planets aspect the
    birth chart (e.g., "Transiting Saturn squares natal Sun" = challenging
    period for identity/ego)
  - `house_comparison` (optional): Where transiting planets fall in the natal
    houses
  - `element_distribution` / `quality_distribution`: Combined analysis

**Use case**: Forecast timing for events, understand current life themes,
predict challenging or favorable periods.

**Example**: "What's happening to John in 2025?" → Transiting Jupiter in his
10th house (career expansion), transiting Saturn square his Sun (identity
challenges, growth through difficulty).

---

## 7. `/api/v5/chart-data/solar-return` - Yearly Birthday Chart

**What it does**: Calculates the chart for the moment when the Sun returns to
its exact natal position (happens once per year, near your birthday). This chart
represents the themes for your upcoming year.

**Returns**:

- `return_type`: "Solar"
- `wheel_type`: "dual" (natal + return) or "single" (return only)
- `chart_data`:
  - If `wheel_type: "dual"`:
    - `first_subject`: Natal chart
    - `second_subject`: Solar return chart
    - `aspects`: Aspects between natal and return charts
  - If `wheel_type: "single"`:
    - `subject`: Just the solar return chart
    - `planets`, `houses`, `aspects`: For the return chart only

**Use case**: Annual forecasting - what themes will dominate this year? What
areas of life will be highlighted?

**Example**: "What will 2025 be like for John?" → Solar return Sun in 5th house
(year focused on creativity, children, romance), return Moon in 10th house
(emotional focus on career).

---

## 8. `/api/v5/chart-data/lunar-return` - Monthly Moon Return

**What it does**: Calculates the chart for when the Moon returns to its exact
natal position (happens approximately every 27 days). Represents themes for the
upcoming month.

**Returns**:

- `return_type`: "Lunar"
- `wheel_type`: "dual" or "single"
- `chart_data`: Same structure as solar return, but for the lunar cycle

**Use case**: Monthly forecasting - what emotional and intuitive themes will
dominate this month?

**Example**: "What's the theme for this month?" → Lunar return Moon in 3rd house
(month focused on communication, learning, siblings), return Venus in 7th house
(month focused on partnerships).

---

## 9. `/api/v5/now/subject` - Current Sky

**What it does**: Returns the astrological positions for the current moment
(right now, UTC time at Greenwich). No birth data needed.

**Returns**:

- `subject`: Current planetary positions
  - `planets`: Where planets are right now
  - `houses`: Current house cusps
  - `lunar_phase`: Current moon phase

**Use case**: Get current planetary positions without needing a birth chart.
Useful for general astrological timing or "what's happening in the sky right
now?"

**Example**: "What's the current astrological weather?" → Sun in Aquarius, Moon
in Pisces, Mercury retrograde, etc.

---

## Common Response Fields Explained

### Planets Object

Each planet entry contains:

- `name`: Planet name (Sun, Moon, Mercury, etc.)
- `sign`: Zodiac sign abbreviation (Ari, Tau, Gem, Can, Leo, Vir, Lib, Sco, Sag,
  Cap, Aqu, Pis)
- `position`: Degree within the sign (0-29.99)
- `abs_pos`: Absolute position in degrees (0-359.99)
- `house`: Which house the planet is in (1st-12th)
- Additional metadata (speed, declination, etc.)

### Aspects Array

Each aspect entry contains:

- `p1_name`, `p2_name`: The two planets involved
- `aspect`: Type of aspect (Conjunction, Sextile, Square, Trine, Opposition,
  etc.)
- `orbit`: How close to exact the aspect is (smaller = more exact/powerful)
- `type`: "major" or "minor" aspect

### Element Distribution

Shows how many planets fall in each element:

- `fire`, `earth`, `air`, `water`: Weighted counts
- `fire_percentage`, etc.: Percentages (0-100)

### Quality Distribution

Shows how many planets fall in each quality:

- `cardinal`, `fixed`, `mutable`: Weighted counts
- `cardinal_percentage`, etc.: Percentages (0-100)

---

## Quick Reference: Which Endpoint to Use?

- **Single person analysis**: `/chart-data/birth-chart`
- **Relationship compatibility**: `/chart-data/synastry` or
  `/compatibility-score`
- **Relationship as entity**: `/chart-data/composite`
- **Current/future influences**: `/chart-data/transit`
- **Yearly forecast**: `/chart-data/solar-return`
- **Monthly forecast**: `/chart-data/lunar-return`
- **Current sky positions**: `/now/subject`
- **Basic planetary positions**: `/subject`
