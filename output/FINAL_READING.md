# Six-Culture Verified Chart — Final Reading

> Computed symbolic corroboration among traditional systems. Not a scientifically validated forecast; no medical, financial, legal, lifespan or fertility claims.

## 1. Input and sensitivity

- Birth: **2001-05-29T18:20:00+05:30** (Tuesday) = **2001-05-29T12:50:00+00:00** UTC, PGIMER Chandigarh (30.765° N, 76.775° E), `Asia/Kolkata` UTC+05:30, no DST.
- Local apparent solar time 17:59:43; sunset 19:19:17 (59 min after birth) → day chart.
- Ascendant boundaries: Western Asc 16 min of clock time from a sign change; Jyotisha Lagna 13 min; D9 Lagna 2.9 min; D10 Lagna 1.3 min.
- Stable across the ±30 s rounding band: western_asc, western_mc_sign, jyotisha_lagna, lagna_nakshatra_pada, d9_lagna, d10_lagna, moon_nakshatra_pada, bazi_hour_branch_civil, bazi_hour_branch_apparent_solar, ziwei_time_index, sect, d9_all, d10_all.
- Sensitive under the disclosed ±5 min stress band: lagna_nakshatra_pada, d9_lagna, d10_lagna (everything else stable).
- BaZi: birth is 24.09 days after Lixia and 7.09 days before Mangzhong (month pillar secure).
- **Zi Wei leap-month sensitivity:** the date is day 7 of the *leap* 4th lunar month (闰四月初七). Under iztro's default the chart uses month 4 (Ming in 申). Under the school treating the whole leap month as month 5, Ming moves to 酉 and every palace name shifts. Zi Wei claims that differ between the two are marked low-confidence and do not vote.

## 2. Verification

- 55 checks passed, 0 alerts, 0 failures.
- Planet longitudes: Swiss Ephemeris vs JPL DE421/Skyfield max difference 0.010″; Asc/MC vs independent spherical-trig code 0.43″; solar terms ≤ 0.04 s.
- BaZi pillars verified by two separate codebases; Zi Wei is a single method (iztro JS and py-iztro share code); Lahiri ayanamsha value is single-source.
- Unavailable/omitted: jyotisha_shadbala, jyotisha_ashtakavarga, jyotisha_d7_d12, jyotisha_jaimini_kp_alt_ayanamsha, western_zodiacal_releasing, western_transits, western_modern_outer_planets_patterns, tibetan_mewa_parkha_forces, maya_day_sign_meanings, tibetan_symbolic_meanings, de440_kernel, online_geocoding.

## 3. Divergence rate (read this first)

- Divergent domains: **3 / 9 = 33%**; over domains with sufficient evidence: 3 / 9 = 33%.
- No domain reached STRONG (all three clusters agreeing). D1 Self/identity: WEAK, D2 Career/status: WEAK, D3 Wealth/gains: MODERATE, D4 Partnership: DIVERGENT, D5 Family/roots/home: DIVERGENT, D6 Children/creation: WEAK, D7 Health/routine: WEAK, D8 Mind/education/craft: DIVERGENT, D9 Fortune/spirituality/worldview: WEAK.

## 4. Cross-cultural themes (MODERATE and above)

### D3 Wealth/gains — MODERATE (shared polarity: mixed)
- **Jyotisha** high / mixed (score +0) — H2 Sagittarius: lord Jupiter dignity enemy_sign (-0.5), lord Jupiter in house 7 (kendra/trikona) (+0.5), occupant Mars (natural malefic) (-0.5), occupant Ketu (natural malefic) (-0.5); H11 Virgo: lord Mercury dignity own (+1), lord Mercury in house 8 (dusthana) (-0.5), Jupiter drishti (+0.5)
- **Western** medium / challenging (score -2.5) — H2 Sagittarius: ruler Jupiter in detriment (-1), ruler Jupiter in bad place (house 8) (-0.5), ruler Jupiter under_the_beams (-0.5), occupant Mars contrary malefic (-1); H11 Virgo: ruler Mercury in domicile (+1), ruler Mercury in bad place (house 8) (-0.5), occupant Moon (neutral in this rule) (+0)
- **Sinic** high / mixed — Zi Wei 财帛 Wealth: 破军 brightness 旺 (conf medium) | BaZi Indirect Wealth (weight 2.0; elements {'Fire': 'challenging'}; conf medium)

Reading of D3: jyotisha and sinic agree the domain is mixed in polarity; western (challenging) differs without direct conflict. 'Mixed' means supportive and difficult factors coexist under the registry rules; this is agreement on emphasis, not a promise of gain or loss.

## 5. Disagreements

### D4 Partnership — DIVERGENT
- **Jyotisha** high / supportive (score +1) — H7 Taurus: lord Venus dignity exalted (+1), lord Venus in house 5 (kendra/trikona) (+0.5), occupant Sun (natural malefic) (-0.5), occupant Jupiter (natural benefic) (+0.5), occupant Saturn (natural malefic) (-0.5)
- **Western** low / challenging (score -1.5) — H7 Taurus: ruler Venus in detriment (-1), ruler Venus in bad place (house 6) (-0.5)
- **Sinic** high / challenging — Zi Wei 夫妻 Spouse: 武曲 brightness 旺, 天府 brightness 旺 (conf low) | BaZi Indirect Wealth (weight 2.0; elements {'Fire': 'challenging'}; conf medium)
- (Zi Wei, low confidence, not voting: high / supportive; leap-month alternative differs.)

### D5 Family/roots/home — DIVERGENT
- **Jyotisha** medium / mixed (score +0) — H4 Aquarius: lord Saturn dignity friend_sign (+0.5), lord Saturn in house 7 (kendra/trikona) (+0.5), lord Saturn combust (-0.5), Saturn drishti (-0.5)
- **Western** low / challenging (score -1) — H4 Aquarius: ruler Saturn in bad place (house 8) (-0.5), ruler Saturn combust (-0.5)
- **Sinic** high / supportive — Zi Wei 父母 Parents: 天机 brightness 旺, 巨门 brightness 庙, 巨门 化禄; 田宅 Property: 天梁 brightness 陷 (conf medium)

### D8 Mind/education/craft — DIVERGENT
- **Jyotisha** low / supportive (score +1) — H3 Capricorn: lord Saturn dignity friend_sign (+0.5), lord Saturn in house 7 (kendra/trikona) (+0.5), lord Saturn combust (-0.5), Jupiter drishti (+0.5)
- **Western** low / challenging (score -1) — H3 Capricorn: ruler Saturn in bad place (house 8) (-0.5), ruler Saturn combust (-0.5)
- **Sinic** high / supportive — BaZi Direct Resource, Indirect Resource (weight 2.6; elements {'Metal': 'supportive'}; conf medium)

## 6. Weak and insufficient domains (do not over-read)

- **D1 Self/identity — WEAK**: speaking clusters ['jyotisha', 'sinic']; jyotisha medium/mixed (high); western low/mixed (high); sinic medium/supportive (medium)
- **D2 Career/status — WEAK**: speaking clusters ['jyotisha']; jyotisha medium/mixed (high); western low/mixed (high); sinic high/mixed (low)
- **D6 Children/creation — WEAK**: speaking clusters ['jyotisha', 'western']; jyotisha medium/mixed (high); western low/challenging (high); sinic medium/mixed (low)
- **D7 Health/routine — WEAK**: speaking clusters ['western']; jyotisha low/mixed (high); western medium/supportive (high)
- **D9 Fortune/spirituality/worldview — WEAK**: speaking clusters ['jyotisha']; jyotisha medium/supportive (high); western low/mixed (high); sinic high/mixed (low)

Safety scope: the 8th house is deliberately unmapped in both Jyotisha and Western. In this chart it holds Mercury and Rahu (sidereal) and Sun, Mercury, Jupiter and Saturn (tropical); that emphasis is recorded in the dataset but not projected onto any life domain.

## 7. Temperament overlay

| Axis | Clusters indicating | Jyotisha | Western | Sinic |
|---|---|---|---|---|
| T1 Leadership/visibility | 2/3 | ✔ Sun: house 7, enemy_sign | – Sun: house 8 (succedent), peregrine | ✔ Ming stars primary ['贪狼'], alt-school ['天机', '巨门']; visible stem gods ['正印', '劫财', '正官'] |
| T2 Drive/initiative | 1/3 | – Mars: house 2, friend_sign | – Mars: house 2 (succedent), minor_dignity_only | ✔ Ming stars primary ['贪狼'], alt-school ['天机', '巨门']; visible stem gods ['正印', '劫财', '正官'] |
| T3 Nurturing/service | 2/3 | ✔ Moon: house 10, friend_sign | – Moon: house 11 (succedent), peregrine | ✔ Ming stars primary ['贪狼'], alt-school ['天机', '巨门']; visible stem gods ['正印', '劫财', '正官'] |
| T4 Intellect/craft | 2/3 | ✔ Mercury own, combust=False | ✔ Mercury domicile, free_of_beams | – Ming stars primary ['贪狼'], alt-school ['天机', '巨门']; visible stem gods ['正印', '劫财', '正官'] |
| T5 Adaptability | 1/3 | – Lagna Scorpio | – Asc Scorpio | ✔ Ming primary 申 ['贪狼'], alt 酉 ['天机', '巨门'] |
| T6 Discipline/structure | 2/3 | ✔ Saturn: house 7, friend_sign | – Saturn: house 8 (succedent), minor_dignity_only | ✔ Ming stars primary ['贪狼'], alt-school ['天机', '巨门']; visible stem gods ['正印', '劫财', '正官'] |

No axis is indicated by all three clusters. Two-cluster axes: Leadership/visibility (jyotisha + sinic), Nurturing/service (jyotisha + sinic), Intellect/craft (jyotisha + western), Discipline/structure (jyotisha + sinic).
- Maya (symbolic, non-voting): Long Count 12.19.8.4.16, Calendar Round 5 K'ib' 14 Sip. Day-sign meaning omitted — no named Maya source available to attribute.
- Tibetan (symbolic, non-voting): female Iron-Snake year. Mewa, Parkha and personal forces omitted (not validated); meanings omitted (no sourced text).

## 8. Timing

Reference date 2026-11-09. Active periods:
- Jyotisha: Mahadasha Sun (2023-07-29 – 2029-07-29), Antardasha Saturn (2026-06-04 – 2027-05-17), Pratyantardasha Venus (2026-10-06 – 2026-12-03).
- Western: profection age 25 → house 2 (Sagittarius), lord of year Jupiter (natal house 8, detriment). 2026 solar return Asc: Birthplace Sagittarius, Chandigarh Sagittarius, Gurugram Sagittarius (location changes sign: False).
- BaZi: Da Yun 辛卯 (until 2029-06-08); annual 丙午.
- Zi Wei: decadal palace 午 夫妻; yearly palace 午 (夫妻 / alt-school 子女 — differs, so not used for votes).

**Base rate first:** with these activation rules, each domain has a 6.3% chance per segment of being hit by ≥2 clusters by coincidence (≈0.56 moderate windows expected per segment). The windows below are therefore roughly at chance level and should be treated as weak signals.

| Domain | Start | End | Clusters | Grade |
|---|---|---|---|---|
| D3 Wealth/gains | 2026-11-09 | 2027-05-17 | western, sinic | moderate |
| D4 Partnership | 2026-11-09 | 2027-05-17 | jyotisha, sinic | moderate |
| D3 Wealth/gains | 2027-05-17 | 2027-05-29 | jyotisha, western, sinic | strong |
| D3 Wealth/gains | 2027-05-29 | 2028-02-04 | jyotisha, sinic | moderate |
| D6 Children/creation | 2029-05-29 | 2029-07-29 | jyotisha, western | moderate |
| D2 Career/status | 2029-07-29 | 2030-02-03 | jyotisha, sinic | moderate |
| D3 Wealth/gains | 2030-05-29 | 2030-12-28 | jyotisha, western | moderate |
| D7 Health/routine | 2030-05-29 | 2030-12-28 | jyotisha, western | moderate |
| D3 Wealth/gains | 2033-05-29 | 2033-10-28 | jyotisha, western | moderate |
| D3 Wealth/gains | 2035-05-29 | 2036-05-29 | jyotisha, western | moderate |

Current: D3 Wealth/gains (moderate, western + sinic, 2026-11-09 – 2027-05-17); D4 Partnership (moderate, jyotisha + sinic, 2026-11-09 – 2027-05-17)
Next: D3 Wealth/gains (strong, jyotisha + western + sinic, 2027-05-17 – 2027-05-29)
Note: the strong window D3 2027-05-17 – 2027-05-29 lasts only 12 days and arises from adjacent period boundaries; do not read it as a significant event window.

## 9. Removed candidate claims

- missing_basis: 2
- low_confidence: 7
- duplication: 0
- safety_scope: 2

## 10. Closing frame

This reading reports where traditional symbolic systems, computed with declared conventions and independently checked arithmetic, agree or disagree. The calculations are reproducible; the meanings are traditional symbolism, not established causation. Agreement here is mostly weak or at chance level, and a third of the domains disagree outright. Nothing in this document is a prediction, guarantee, or basis for medical, financial, legal or family decisions.
