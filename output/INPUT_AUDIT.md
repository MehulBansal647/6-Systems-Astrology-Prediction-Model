# Input Audit

## Original input (unchanged)

- **date_of_birth**: 29/05/2001
- **time_of_birth**: 6:20 PM
- **time_certainty**: Exact Time
- **birthplace**: PGI Chandigarh, India
- **gender**: Male
- **current_residence**: Permanent Parental Home - Chandigarh, Job -Gurugram
- **calendar_note**: none given (assumed Gregorian civil date)
- **dst_or_timezone_uncertainty_note**: none given

## Normalized

- Gregorian civil date/time: **2001-05-29T18:20:00+05:30** (Tuesday)
- UTC instant: **2001-05-29T12:50:00+00:00**
- IANA zone: `Asia/Kolkata` (timezonefinder lookup: `Asia/Kolkata`), tzdata 2026.6
- Offset 5:30:00, DST 0:00:00, fold ambiguity: False
- Historical offsets sampled: 1942-06-01 5:30:00; 1945-06-01 6:30:00; 1946-06-01 5:30:00; 1971-06-01 5:30:00; 1990-06-01 5:30:00; 2001-06-01 5:30:00; 2026-06-01 5:30:00
  - IST (UTC+05:30) has applied without DST since 1945; 2001 is in the post-1970 reliable tzdb range.
- Coordinates: 30.765° N, 76.775° E — Reference coordinates for the PGIMER campus (no live geocoder reachable from the sandbox); estimated accuracy about 0.005 deg (~0.5 km). Elevation not reliably available; calculations use 0 m (sea-level horizon).
- Julian Day UT 2452059.034722; TT 2452059.035465; ΔT 64.18 s
- Local mean time: 2001-05-29T17:57:06
- Equation of time: +2.62 min → local apparent solar time: 2001-05-29T17:59:43.159360
- Sunrise: 2001-05-29T05:21:27.889440+05:30; Sunset: 2001-05-29T19:19:17.302393+05:30 (birth 59.3 min before sunset)
- Calendar: Gregorian civil date; no other calendar conversion was required.

## Time-uncertainty ensemble

Primary band ±0.5 min (rounding interval of a minute-exact record). Stress band ±5 min is a disclosed sensitivity check, not rectification. Ascendant moves ≈0.211°/min.

| Datum | ±0.5 min | ±5 min |
|---|---|---|
| western_asc | stable | stable |
| western_mc_sign | stable | stable |
| jyotisha_lagna | stable | stable |
| lagna_nakshatra_pada | stable | sensitive |
| d9_lagna | stable | sensitive |
| d10_lagna | stable | sensitive |
| moon_nakshatra_pada | stable | stable |
| bazi_hour_branch_civil | stable | stable |
| bazi_hour_branch_apparent_solar | stable | stable |
| ziwei_time_index | stable | stable |
| sect | stable | stable |
| d9_all | stable | stable |
| d10_all | stable | stable |

| Instant | Local | West Asc | Jyotisha Lagna | D9 Lagna | D10 Lagna | Lagna pada | BaZi hour (civil/LAST) | Zi Wei idx |
|---|---|---|---|---|---|---|---|---|
| T-unc | 18:19:30 | Scorpio | Scorpio | Cancer | Cancer | Vishakha 4 | 酉/酉 | 9 |
| T | 18:20:00 | Scorpio | Scorpio | Cancer | Cancer | Vishakha 4 | 酉/酉 | 9 |
| T+unc | 18:20:30 | Scorpio | Scorpio | Cancer | Cancer | Vishakha 4 | 酉/酉 | 9 |
| T-stress | 18:15:00 | Scorpio | Scorpio | Cancer | Cancer | Vishakha 4 | 酉/酉 | 9 |
| T+stress | 18:25:00 | Scorpio | Scorpio | Leo | Leo | Anuradha 1 | 酉/酉 | 9 |

## Boundary audit

| Boundary | Distance | Would change |
|---|---|---|
| Western Ascendant sign (Scorpio/Sagittarius) | 3.404° / 16.2 min | all whole-sign houses, profections, Lots' houses |
| Jyotisha Lagna sign (Libra/Scorpio) | 2.724° / 12.9 min | all houses, house lords, functional natures, yogas |
| Jyotisha D9 Lagna boundary | 0.610° / 2.9 min | D9 Lagna |
| Jyotisha D10 Lagna boundary | 0.276° / 1.3 min | D10 Lagna |
| Sunset / sect | 59.3 min | sect (day->night), Lot formulas, benefic/malefic of sect |
| BaZi/Zi Wei two-hour (酉 ends 19:00 civil) | 40.0 min | hour pillar, Zi Wei Ming/Shen and hour stars |
| BaZi 酉 start (17:00) in apparent solar time | 59.7 min | hour pillar under apparent-solar-time school |
| Day boundary (late Zi 23:00 / midnight) | 280.0 min | day pillar (late-Zi school), Zi Wei day |
| Mangzhong sectional term (Si->Wu month) | 7.086 days | month pillar, Da Yun |
| Lixia sectional term | 24.087 days | month pillar |
| Lunar leap month (闰四月 day 7) | convention-dependent (see verification) | Zi Wei Ming palace and star layout under the 'leap month = next month' school (see verification) |
| Tibetan Losar 2001 | > 90 days | Tibetan year element-animal |
| Gregorian adoption | n/a (2001) days | none |
| Moon nakshatra/pada edge | 0.792° | Moon pada; Vimshottari start lord only at nakshatra edge |
