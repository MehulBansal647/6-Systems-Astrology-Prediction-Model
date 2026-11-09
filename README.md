# Six-Culture Verified Chart

A reproducible computation, verification, and synthesis of one birth chart across Jyotisha, BaZi, Western/Hellenistic, Zi Wei Dou Shu, the Maya calendar, and Tibetan elemental astrology. The results are symbolic corroboration among traditional systems. They are **not** a validated forecast.

## Layout

| Path | Purpose |
|---|---|
| `BIRTH_INPUT.json` | Original and normalized input. Calculation code contains no personal data. |
| `config/mapping_registry.json` | Mapping rules (domains, polarity, timing, temperament), fixed before projection |
| `src/astro_core.py` | Swiss Ephemeris (primary) and Skyfield + JPL DE421 (validator) |
| `src/jyotisha.py`, `src/western.py`, `src/bazi.py`, `src/calendars.py`, `src/ziwei_iztro.js` | Per-system calculations (facts only) |
| `src/build_dataset.py` | Audit, uncertainty ensemble, verification, master dataset |
| `src/synthesize.py` | Domain grading by primary cluster, temperament, chronology |
| `src/report.py` | Markdown rendering (adds no new facts) |
| `output/` | `INPUT_AUDIT.md`, `CALCULATION_MANIFEST.json`, `MASTER_DATASET.{json,md}`, `VERIFICATION_REPORT.{json,md}`, `SYNTHESIS.json`, `FINAL_READING.md` |

## Reproduce

```bash
./run_all.sh
```

Requires Python 3.12 and Node.js. Package versions are pinned in `requirements.lock` and `js/package-lock.json`. Ephemeris file checksums are recorded in `output/CALCULATION_MANIFEST.json`. The reference date for timing (`REFERENCE_DATE` in `src/build_dataset.py`) is 2026-11-09.

## Known limitations

- The JPL DE440 download was blocked, so the validator uses DE421 from the `skyfield-data` package.
- Geocoding was blocked, so the code uses reference coordinates for PGIMER Chandigarh (about 0.5 km accuracy).
- Zi Wei is a single method: py-iztro wraps iztro, so comparing them only checks the interface. The birth falls in a lunar leap month, and the result is reported under two leap-month conventions.
- Shadbala, Ashtakavarga, zodiacal releasing, Mewa, Parkha, Tibetan personal forces, and Maya/Tibetan symbolic meanings are omitted. The reasons are in `excluded_methods`.
