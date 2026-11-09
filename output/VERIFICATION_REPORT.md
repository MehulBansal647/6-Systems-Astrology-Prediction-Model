# Verification Report

Counts: {'pass': 55}. Failed systems: none.

- Largest planet longitude difference (Swiss Ephemeris vs JPL DE421/Skyfield): 0.0105″
- Asc/MC difference (Swiss vs independent spherical-trig code): 0.43″
- Solar-term instant max difference: 0.041 s

Independence disclosures:
- Swiss Ephemeris files are compressed from JPL DE431; the validator uses JPL DE421 via Skyfield. Different reduction code, related JPL lineage.
- The Lahiri ayanamsha value is single-source (Swiss Ephemeris); sidereal checks validate the tropical part only.
- iztro (JS) and py-iztro are the SAME method; their comparison is an interface check only. Zi Wei is single-method.
- BaZi pillars: lunar_python vs. independent JDN/solar-longitude arithmetic written here (genuinely separate code).

| System | Datum | Primary | Validator | Diff | Stability | Confidence | Status |
|---|---|---|---|---|---|---|---|
| shared | Sunrise (birth morning, upper limb, standard refraction) | 2001-05-28T23:51:27.889440+00:00 | 2001-05-28T23:51:24.682458+00:00 | 3.206982 | stable | high | pass |
| shared | Sunset (birth evening) | 2001-05-29T13:49:17.302393+00:00 | 2001-05-29T13:49:20.574756+00:00 | 3.272363 | stable | high | pass |
| shared | Sun true altitude at birth | 10.947424 | 10.945166 | 0.002258 | stable | high | pass |
| shared | IANA zone from coordinates | Asia/Kolkata | Asia/Kolkata | 0 | stable | high | pass |
| shared | Sun tropical apparent longitude | 68.211958 | 68.211958 | 0.000000 | stable | high | pass |
| shared | Moon tropical apparent longitude | 153.079702 | 153.079702 | 0.000000 | stable | high | pass |
| shared | Mercury tropical apparent longitude | 88.717317 | 88.717317 | 0.000000 | stable | high | pass |
| shared | Venus tropical apparent longitude | 22.783274 | 22.783274 | 0.000000 | stable | high | pass |
| shared | Mars tropical apparent longitude | 267.046676 | 267.046675 | 0.000000 | stable | high | pass |
| shared | Jupiter tropical apparent longitude | 79.832934 | 79.832933 | 0.000000 | stable | high | pass |
| shared | Saturn tropical apparent longitude | 64.880112 | 64.880112 | 0.000000 | stable | high | pass |
| shared | Uranus tropical apparent longitude | 324.837677 | 324.837679 | 0.000003 | stable | high | pass |
| shared | Neptune tropical apparent longitude | 308.685505 | 308.685506 | 0.000001 | stable | high | pass |
| shared | Pluto tropical apparent longitude | 254.082124 | 254.082125 | 0.000001 | stable | high | pass |
| shared | Asc tropical | 236.595558 | 236.595463 | 0.000095 | stable | high | pass |
| shared | MC tropical | 154.524527 | 154.524406 | 0.000120 | stable | high | pass |
| jyotisha | Sun sidereal longitude (Lahiri) | 44.340114 | 44.340115 | 0.000000 | stable | high | pass |
| jyotisha | Moon sidereal longitude (Lahiri) | 129.207858 | 129.207858 | 0.000000 | stable | high | pass |
| jyotisha | Mars sidereal longitude (Lahiri) | 243.174832 | 243.174832 | 0.000000 | stable | high | pass |
| jyotisha | Mercury sidereal longitude (Lahiri) | 64.845473 | 64.845473 | 0.000000 | stable | high | pass |
| jyotisha | Jupiter sidereal longitude (Lahiri) | 55.961090 | 55.961090 | 0.000000 | stable | high | pass |
| jyotisha | Venus sidereal longitude (Lahiri) | 358.911430 | 358.911431 | 0.000000 | stable | high | pass |
| jyotisha | Saturn sidereal longitude (Lahiri) | 41.008268 | 41.008268 | 0.000000 | stable | high | pass |
| jyotisha | Lagna sign | Scorpio | Scorpio | 0.000095 | stable | high | pass |
| jyotisha | Rahu-Ketu separation (mean node) | 180.000000 | 180.000000 | 0.000000 | stable | high | pass |
| jyotisha | Vimshottari cycle total years | 120 | 120 | 0 | stable | high | pass |
| jyotisha | Vimshottari periods continuous/ordered/non-overlapping | true | true | 0 | stable | high | pass |
| western | Ascendant sign (tropical) | Scorpio | Scorpio | 0.000095 | stable | high | pass |
| western | Sect (day chart) | true | True | 0 | stable | high | pass |
| bazi | Solar term Lichun (315) 2001 | 2001-02-03T18:28:49.645617+00:00 | 2001-02-03T18:28:49.631884+00:00 | 0.013733 | stable | high | pass |
| bazi | Solar term Lixia (45, jie opening Si month) 2001 | 2001-05-05T10:44:49.706983+00:00 | 2001-05-05T10:44:49.748182+00:00 | 0.041199 | stable | high | pass |
| bazi | Solar term Xiaoman (60, zhongqi) 2001 | 2001-05-20T23:44:11.896231+00:00 | 2001-05-20T23:44:11.882498+00:00 | 0.013733 | stable | high | pass |
| bazi | Solar term Mangzhong (75, jie opening Wu month) 2001 | 2001-06-05T14:53:35.681264+00:00 | 2001-06-05T14:53:35.667531+00:00 | 0.013733 | stable | high | pass |
| bazi | Birth after Lixia and before Mangzhong (Si month) | true | true | 0 | stable | high | pass |
| bazi | year pillar (civil local time) | 辛巳 | 辛巳 | 0 | stable | high | pass |
| bazi | month pillar (civil local time) | 癸巳 | 癸巳 | 0 | stable | high | pass |
| bazi | day pillar (civil local time) | 壬辰 | 壬辰 | 0 | stable | high | pass |
| bazi | hour pillar (civil local time) | 己酉 | 己酉 | 0 | stable | high | pass |
| bazi | Hidden stems (set per branch) | {"year": ["丙", "庚", "戊"], "month": ["丙", "庚", "戊"], "day"… | {"year": "丙戊庚", "month": "丙戊庚", "day": "戊乙癸", "hour": "辛"} | 0 | stable | high | pass |
| bazi | Da Yun direction and pillar sequence | ["壬辰", "辛卯", "庚寅", "己丑", "戊子"] | ["壬辰", "辛卯", "庚寅", "己丑", "戊子"] | 0 | stable | high | pass |
| bazi | Da Yun start instant | 2009-06-08T23:10:35.162040+00:00 | 2009-06-09T01:19:27.288058+00:00 | 0.089492 | stable | medium | pass |
| bazi | Da Yun periods continuous | true | true | 0 | stable | high | pass |
| ziwei | Ming branch, bureau, major-star layout | {"ming": "申", "bureau": "火六局"} | {"ming": "申", "bureau": "火六局"} | 0 | stable | medium | pass |
| ziwei | 12 unique palaces | 12 | 12 | 0 | stable | high | pass |
| ziwei | 14 major stars each placed once | 14 | 14 | 0 | stable | high | pass |
| ziwei | Tian Fu mirrors Zi Wei across Yin-Shen axis | 午 | 午 | 0 | stable | high | pass |
| ziwei | Ming/Shen palace branches | ["申", "寅"] | ["申", "寅"] | 0 | stable | high | pass |
| ziwei | Leap-month convention sensitivity | {"ming": "申", "bureau": "火六局"} | {"ming": "酉", "bureau": "火六局"} | 1 | sensitive | low | pass |
| ziwei | Decadal ranges continuous | [6, 15, "申"] | [116, 125, "酉"] | 0 | stable | high | pass |
| maya | Long Count | [12, 19, 8, 4, 16] | [12, 19, 8, 4, 16] | 0 | stable | high | pass |
| maya | Tzolk'in | [5, "K'ib'"] | [5, "K'ib'"] | 0 | stable | high | pass |
| maya | Haab' | [14, "Zip"] | [14, "Sip"] | 0 | stable | high | pass |
| maya | Round trip to 2001-05-29 | [2001, 5, 29] | [2001, 5, 29] | 0 | stable | high | pass |
| maya | Control date 2012-12-21 | 13.0.0.0.0 4 Ajaw 3 K'ank'in | 13.0.0.0.0 4 Ajaw 3 K'ank'in | 0 | stable | high | pass |
| tibetan | Element-animal year | female Iron-Snake | 辛巳 | 0 | stable | medium | pass |

## Notes

- **Sunset (birth evening)**: 59.3 min before sunset
- **Sun sidereal longitude (Lahiri)**: 14.340 deg to sign edge
- **Moon sidereal longitude (Lahiri)**: 9.208 deg to sign edge
- **Mars sidereal longitude (Lahiri)**: 3.175 deg to sign edge
- **Mercury sidereal longitude (Lahiri)**: 4.845 deg to sign edge
- **Jupiter sidereal longitude (Lahiri)**: 4.039 deg to sign edge
- **Venus sidereal longitude (Lahiri)**: 1.089 deg to sign edge
- **Saturn sidereal longitude (Lahiri)**: 11.008 deg to sign edge
- **Lagna sign**: 2.724 deg (~12.9 min of clock time)
- **Ascendant sign (tropical)**: 3.404 deg (~16.2 min of clock time)
- **Sect (day chart)**: 59.3 min before sunset
- **Solar term Lichun (315) 2001**: +114.7647 days from birth (birth minus term)
- **Solar term Lixia (45, jie opening Si month) 2001**: +24.0869 days from birth (birth minus term)
- **Solar term Xiaoman (60, zhongqi) 2001**: +8.5457 days from birth (birth minus term)
- **Solar term Mangzhong (75, jie opening Wu month) 2001**: -7.0858 days from birth (birth minus term)
- **Birth after Lixia and before Mangzhong (Si month)**: 24.087 d after Lixia; 7.086 d before Mangzhong
- **Hidden stems (set per branch)**: Same stems; middle/residual ORDER differs for 巳 (school variation). DM strength recomputed under both orders.
- **Da Yun start instant**: lunar_python start 2009-05-27 18:20:00 not used (CST-input caveat)
- **Leap-month convention sensitivity**: fixLeap=false gives identical layout: True
- **Element-animal year**: Phugpa Losar date not computed by a validated lineage-specific implementation; the year assignment is robust because the birth date is far from any plausible Losar.

## Excluded / unavailable methods

- `jyotisha_shadbala`: no validated implementation in this environment
- `jyotisha_ashtakavarga`: timing/transit support not requested; omitted
- `jyotisha_d7_d12`: domains not specifically requested
- `jyotisha_jaimini_kp_alt_ayanamsha`: separate tracks not requested; not computed
- `western_zodiacal_releasing`: implementation not validated
- `western_transits`: only profection and solar return used for timing
- `western_modern_outer_planets_patterns`: reported as separate optional track only (no votes)
- `tibetan_mewa_parkha_forces`: not validated (see tibetan.omitted)
- `maya_day_sign_meanings`: no named historical/living Maya source available to attribute; meanings omitted
- `tibetan_symbolic_meanings`: no sourced lineage text available; meanings omitted
- `de440_kernel`: JPL download blocked by network policy; DE421 (skyfield-data package) used as validator
- `online_geocoding`: geocoder blocked; reference coordinates used
