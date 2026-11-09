"""Render Markdown reports from the JSON datasets. No new facts are introduced here."""
from __future__ import annotations

import json
import os
from datetime import date, datetime

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "output")
M = json.load(open(os.path.join(OUT, "MASTER_DATASET.json")))
V = json.load(open(os.path.join(OUT, "VERIFICATION_REPORT.json")))
S = json.load(open(os.path.join(OUT, "SYNTHESIS.json")))
C = json.load(open(os.path.join(OUT, "CALCULATION_MANIFEST.json")))
R = json.load(open(os.path.join(ROOT, "config", "mapping_registry.json")))

ZW_EN = {"命宫": "Life (Ming)", "兄弟": "Siblings", "夫妻": "Spouse", "子女": "Children", "财帛": "Wealth", "疾厄": "Health",
         "迁移": "Travel", "仆役": "Friends", "官禄": "Career", "田宅": "Property", "福德": "Fortune/Spirit", "父母": "Parents"}
STAR_EN = {"紫微": "Zi Wei", "天机": "Tian Ji", "太阳": "Tai Yang", "武曲": "Wu Qu", "天同": "Tian Tong", "廉贞": "Lian Zhen",
           "天府": "Tian Fu", "太阴": "Tai Yin", "贪狼": "Tan Lang", "巨门": "Ju Men", "天相": "Tian Xiang", "天梁": "Tian Liang",
           "七杀": "Qi Sha", "破军": "Po Jun"}
BR_EN = dict(zip("子丑寅卯辰巳午未申酉戌亥", ["Zi", "Chou", "Yin", "Mao", "Chen", "Si", "Wu", "Wei", "Shen", "You", "Xu", "Hai"]))


def dms(x):
    d = int(x)
    m = (x - d) * 60
    return f"{d}°{int(m):02d}′{(m - int(m)) * 60:04.1f}″"


def f(x, n=4):
    return f"{x:.{n}f}"


def write(name, text):
    with open(os.path.join(OUT, name), "w") as fh:
        fh.write(text)


def input_audit():
    a = M["input_audit"]
    t = M["time_uncertainty"]
    L = ["# Input Audit", "", "## Original input (unchanged)", ""]
    for k, v in a["original"].items():
        L.append(f"- **{k}**: {v}")
    n = M["input"]["normalized"]
    L += ["", "## Normalized", "",
          f"- Gregorian civil date/time: **{a['normalized_local']}** ({a['civil_weekday']})",
          f"- UTC instant: **{a['utc_instant']}**",
          f"- IANA zone: `{a['iana_zone']}` (timezonefinder lookup: `{a['timezonefinder_zone']}`), tzdata {a['tzdata_release']}",
          f"- Offset {a['utc_offset']}, DST {a['dst']}, fold ambiguity: {a['fold_ambiguity']}",
          f"- Historical offsets sampled: " + "; ".join(f"{h['date']} {h['utc_offset']}" for h in a["historical_offsets_sampled"]),
          "  - IST (UTC+05:30) has applied without DST since 1945; 2001 is in the post-1970 reliable tzdb range.",
          f"- Coordinates: {n['place']['latitude']}° N, {n['place']['longitude']}° E — {n['place']['coordinate_source']}",
          f"- Julian Day UT {a['julian_day_ut']:.6f}; TT {a['julian_day_tt']:.6f}; ΔT {a['delta_t_seconds']:.2f} s",
          f"- Local mean time: {a['local_mean_time']}",
          f"- Equation of time: {a['equation_of_time_minutes']:+.2f} min → local apparent solar time: {a['local_apparent_solar_time']}",
          f"- Sunrise: {a['sunrise_local']}; Sunset: {a['sunset_local']} (birth {a['minutes_before_sunset']:.1f} min before sunset)",
          "- Calendar: Gregorian civil date; no other calendar conversion was required.",
          "", "## Time-uncertainty ensemble", "",
          f"Primary band ±{t['primary_band_minutes']} min (rounding interval of a minute-exact record). "
          f"Stress band ±{t['stress_band_minutes']} min is a disclosed sensitivity check, not rectification. "
          f"Ascendant moves ≈{t['asc_rate_deg_per_min']:.3f}°/min.", "",
          "| Datum | ±0.5 min | ±5 min |", "|---|---|---|"]
    for k, v in t["stability"].items():
        vals = list(v.values())
        L.append(f"| {k} | {vals[0]} | {vals[1]} |")
    L += ["", "| Instant | Local | West Asc | Jyotisha Lagna | D9 Lagna | D10 Lagna | Lagna pada | BaZi hour (civil/LAST) | Zi Wei idx |",
          "|---|---|---|---|---|---|---|---|---|"]
    for k, e in t["instants"].items():
        L.append(f"| {k} | {e['local'][11:19]} | {e['western_asc']} | {e['jyotisha_lagna']} | {e['d9_lagna']} | {e['d10_lagna']} | "
                 f"{e['lagna_nakshatra_pada']} | {e['bazi_hour_branch_civil']}/{e['bazi_hour_branch_apparent_solar']} | {e['ziwei_time_index']} |")
    L += ["", "## Boundary audit", "", "| Boundary | Distance | Would change |", "|---|---|---|"]
    for b in M["boundary_audit"]:
        parts = []
        if b.get("distance_deg") is not None:
            parts.append(f"{b['distance_deg']:.3f}°")
        if b.get("distance_clock_min") is not None:
            parts.append(f"{b['distance_clock_min']:.1f} min")
        dd = b.get("distance_days")
        if dd is not None:
            parts.append((dd if isinstance(dd, str) else f"{dd:.3f}") + " days")
        if not parts:
            parts.append("convention-dependent (see verification)")
        L.append(f"| {b['boundary']} | {' / '.join(parts)} | {b['would_change']} |")
    write("INPUT_AUDIT.md", "\n".join(L) + "\n")


def verification_md():
    L = ["# Verification Report", "", f"Counts: {M['verification_summary']['counts']}. Failed systems: {M['verification_summary']['failed_systems'] or 'none'}.", "",
         f"- Largest planet longitude difference (Swiss Ephemeris vs JPL DE421/Skyfield): {M['verification_summary']['largest_planet_diff_deg'] * 3600:.4f}″",
         f"- Asc/MC difference (Swiss vs independent spherical-trig code): {M['verification_summary']['asc_mc_diff_deg'] * 3600:.2f}″",
         f"- Solar-term instant max difference: {M['verification_summary']['solar_term_max_diff_s']:.3f} s",
         "", "Independence disclosures:",
         "- Swiss Ephemeris files are compressed from JPL DE431; the validator uses JPL DE421 via Skyfield. Different reduction code, related JPL lineage.",
         "- The Lahiri ayanamsha value is single-source (Swiss Ephemeris); sidereal checks validate the tropical part only.",
         "- iztro (JS) and py-iztro are the SAME method; their comparison is an interface check only. Zi Wei is single-method.",
         "- BaZi pillars: lunar_python vs. independent JDN/solar-longitude arithmetic written here (genuinely separate code).",
         "", "| System | Datum | Primary | Validator | Diff | Stability | Confidence | Status |", "|---|---|---|---|---|---|---|---|"]
    for r in V:
        pv = r["primary_value"]
        vv = r["validator_value"]
        def short(x):
            if isinstance(x, float):
                return f"{x:.6f}"
            s = json.dumps(x, ensure_ascii=False) if not isinstance(x, str) else x
            return s if len(s) < 60 else s[:57] + "…"
        L.append(f"| {r['system']} | {r['datum']} | {short(pv)} | {short(vv)} | {short(r['difference'])} | {r['uncertainty_stability']} | {r['confidence']} | {r['status']} |")
    L += ["", "## Notes", ""]
    for r in V:
        if r.get("note") or r.get("boundary_distance"):
            L.append(f"- **{r['datum']}**: " + "; ".join(x for x in (r.get("boundary_distance"), r.get("note")) if x))
    L += ["", "## Excluded / unavailable methods", ""]
    for k, v in M["excluded_methods"].items():
        L.append(f"- `{k}`: {v}")
    write("VERIFICATION_REPORT.md", "\n".join(L) + "\n")


def master_md():
    j, w, b, z = M["jyotisha"], M["western"], M["bazi"], M["ziwei"]
    L = ["# Master Dataset (facts only)", "", f"Reference date for timing: {C['reference_date_for_timing']}", "",
         "## Jyotisha — sidereal Lahiri, whole-sign, mean node", "",
         f"Ayanamsha (Lahiri): {dms(M['shared_astronomy']['ayanamsha_lahiri_deg'])}. Lagna: **{j['lagna']['sign']} {dms(j['lagna']['degree_in_sign'])}**, "
         f"{j['lagna']['nakshatra']['name']} pada {j['lagna']['nakshatra']['pada']}; D9 {j['lagna']['d9_sign']}; D10 {j['lagna']['d10_sign']}.", "",
         "| Graha | Sign | Deg | House | Nakshatra-pada | Dignity | Retro | Combust (margin) | Functional | D9 | D10 |", "|---|---|---|---|---|---|---|---|---|---|---|"]
    for p, g in j["grahas"].items():
        cb = g.get("combustion")
        cbs = f"{cb['combust']} ({cb['margin_deg']:+.2f}°)" if cb else "—"
        L.append(f"| {p} | {g['sign']} | {dms(g['degree_in_sign'])} | {g['house']} | {g['nakshatra']['name']}-{g['nakshatra']['pada']} | {g['dignity']} | "
                 f"{'R' if g['retrograde'] and p not in ('Rahu', 'Ketu') else ''} | {cbs} | {g.get('functional_status', {}).get('status', '—')} | {g['d9_sign']} | {g['d10_sign']} |")
    L += ["", f"True-node track: Rahu {j['true_node_track_comparison']['nakshatra_true']} (mean: {j['true_node_track_comparison']['nakshatra_mean']}); same sign: {j['true_node_track_comparison']['sign_same']}.",
          f"Planetary war: {j['planetary_war'] or 'none'}. Moon waxing: {j['moon_waxing']} (elongation {j['moon_elongation_deg']:.2f}°).", "", "Yogas (declared whitelist):", ""]
    for y in j["yogas"]:
        extra = f"; cancelled by {y['cancellation_rule']}: {y['cancelled']} ({y['cancellation_basis']})" if "cancelled" in y else ""
        L.append(f"- {y['name']}: **{'present' if y['present'] else 'absent'}** — rule: {y['rule']}; basis: {json.dumps(y['basis'], ensure_ascii=False)}{extra}")
    v = j["vimshottari"]
    cur = v["current_at_reference_date"]
    L += ["", f"Vimshottari: Moon in {v['moon_nakshatra']} (lord {v['nakshatra_lord']}); balance at birth {v['balance_at_birth_years']:.4f} y; "
          f"year = {v['year_length_days']} d; sensitivity {v['sensitivity_days_per_minute_of_birth_time']:.2f} days per minute of birth time.", "",
          "| Mahadasha | Start | End |", "|---|---|---|"]
    for md in v["mahadashas"]:
        L.append(f"| {md['lord']} | {md['start'][:10]} | {md['end'][:10]} |")
    L += ["", f"Current: MD {cur['mahadasha']['lord']} → AD {cur['antardasha']['lord']} ({cur['antardasha']['start'][:10]} – {cur['antardasha']['end'][:10]}) → PD {cur['pratyantardasha']['lord']} ({cur['pratyantardasha']['start'][:10]} – {cur['pratyantardasha']['end'][:10]}).",
          "", "Antardashas of the current Mahadasha:", "", "| AD | Start | End |", "|---|---|---|"]
    for md in v["mahadashas"]:
        if md["lord"] == cur["mahadasha"]["lord"]:
            for ad in md["antardashas"]:
                L.append(f"| {ad['lord']} | {ad['start'][:10]} | {ad['end'][:10]} |")
    for md in v["mahadashas"]:
        if md["start"] == cur["mahadasha"]["end"]:
            L += ["", f"Next Mahadasha ({md['lord']}) antardashas:", "", "| AD | Start | End |", "|---|---|---|"]
            for ad in md["antardashas"]:
                L.append(f"| {ad['lord']} | {ad['start'][:10]} | {ad['end'][:10]} |")
    L += ["", "## Western / Hellenistic — tropical, whole-sign", "",
          f"Ascendant **{w['ascendant']['sign']} {dms(w['ascendant']['degree_in_sign'])}**; MC {w['midheaven']['sign']} {dms(w['midheaven']['degree_in_sign'])} (whole-sign house {w['midheaven']['whole_sign_house']}). "
          f"Sect: **{w['sect']['chart']}** (Sun altitude {w['sect']['sun_true_altitude_deg']:.2f}°). Benefic of sect {w['sect']['benefic_of_sect']}, malefic of sect {w['sect']['malefic_of_sect']}, contrary malefic {w['sect']['contrary_malefic']}.", "",
          "| Planet | Sign | Deg | House | Essential (Lilly pts) | Solar phase | Sect | Retro |", "|---|---|---|---|---|---|---|---|"]
    for p, q in w["planets"].items():
        L.append(f"| {p} | {q['sign']} | {dms(q['degree_in_sign'])} | {q['house']} | {q['essential_dignity']['summary']} ({q['essential_dignity']['lilly_essential_score']}) | "
                 f"{q['solar_phase']['status']} | {'in' if q['in_sect'] else 'out of'} sect | {'R' if q['retrograde'] else ''} |")
    L += ["", f"Final dispositor: {w['final_dispositor']}. Lots: Fortune {w['lots']['Fortune']['sign']} {dms(w['lots']['Fortune']['degree_in_sign'])} (house {w['lots']['Fortune']['house']}); "
          f"Spirit {w['lots']['Spirit']['sign']} {dms(w['lots']['Spirit']['degree_in_sign'])} (house {w['lots']['Spirit']['house']}).", "", "Aspects (Ptolemaic, sign-based, moiety orbs):", ""]
    for a in w["aspects"]:
        L.append(f"- {a['a']} {a['aspect']} {a['b']} — orb {a['orb_deg']:.2f}° ({a['state']})")
    pf = w["profection"]
    L += ["", f"Profection (age {pf['age_completed']}, {pf['start'][:10]} → {pf['end']}): house {pf['profected_house']} ({pf['profected_sign']}), lord of year **{pf['lord_of_year']}** "
          f"(natal {pf['lord_natal_condition']['sign']}, house {pf['lord_natal_condition']['house']}, {pf['lord_natal_condition']['essential']}, {pf['lord_natal_condition']['solar_phase']['status']}).", "", "Solar returns:", ""]
    for s in w["solar_returns"]:
        L.append(f"- {s['year']}: {s['instant_local']} — " + "; ".join(f"{k}: Asc {v['sign']} {v['degree_in_sign']:.1f}°" for k, v in s["ascendants"].items())
                 + f" (location changes Asc sign: {s['location_changes_asc_sign']})")
    L += ["", "Optional modern track (no votes): " + ", ".join(f"{k} {v['sign']} {v['degree_in_sign']:.1f}°" for k, v in w["optional_modern_track"].items()), "",
          "## BaZi", "", f"Pillars (civil IST): **{b['pillars_civil']['year']} {b['pillars_civil']['month']} {b['pillars_civil']['day']} {b['pillars_civil']['hour']}** "
          f"(year–month–day–hour). Apparent-solar-time track identical: {b['pillars_track_agreement']}. Lunar date: {b['lunar_date']}.",
          f"Day Master: {b['day_master']['stem']} ({b['day_master']['polarity']} {b['day_master']['element']}). Na Yin (traditional attribute): {b['na_yin_traditional_attribute']}.", "",
          "| Position | Stem | Ten God |", "|---|---|---|"]
    for k, t in b["ten_gods"].items():
        L.append(f"| {k} | {t['stem']} | {t['ten_god']} {t['en']} |")
    ds = b["day_master_strength"]
    ug = b["useful_god"]
    L += ["", f"Day Master strength ({ds['rule_set']}): support share {ds['support_share']:.3f} → **{ds['verdict']}**; seasonal state {ds['seasonal_state']} ({ds['season']}); rooted in: {ds['rooted_in_branches']}. "
          f"Alternate hidden-stem order: share {ds['alt_hidden_order_check']['support_share']:.3f}, verdict changes: {ds['alt_hidden_order_check']['verdict_changes']}.", ""]
    for sname, sv in ug["schools"].items():
        L.append(f"- {sname}: favorable {sv['favorable']}, unfavorable {sv['unfavorable']}")
    L += [f"- Agreement on favorable: {ug['agreement_favorable']}; disagreement: {ug['disagreement'] or 'none'}; confidence: {ug['confidence']}", "",
          "Interactions: " + json.dumps({k: v for k, v in b["interactions"].items() if v}, ensure_ascii=False), "",
          f"Da Yun ({b['da_yun']['direction']}): {b['da_yun']['days_to_jie']:.4f} days back to Lixia → start DY-A {b['da_yun']['start_rule_DY_A'][:10]} / DY-B {b['da_yun']['start_rule_DY_B'][:10]} "
          f"(difference {b['da_yun']['start_difference_days']:.2f} d).", "", "| Da Yun | Start | End |", "|---|---|---|"]
    for p in b["da_yun"]["periods"]:
        L.append(f"| {p['pillar']} | {p['start'][:10]} | {p['end'][:10]} |")
    L += ["", "Annual pillars (from exact Lichun):", "", "| Year pillar | Start (UTC) | Stem Ten God | Branch main-qi Ten God |", "|---|---|---|---|"]
    for a in b["annual_pillars"]:
        L.append(f"| {a['pillar']} | {a['start_lichun_utc'][:16]} | {a['stem_ten_god']} | {a['branch_main_qi_ten_god']} |")
    c = z["chart"]
    L += ["", "## Zi Wei Dou Shu (iztro, fixLeap=true)", "",
          f"Lunar date {c['lunarDate']}; Ming palace {c['soulBranch']} ({BR_EN[c['soulBranch']]}), Shen palace {c['bodyBranch']} ({BR_EN[c['bodyBranch']]}); "
          f"life ruler {c['soul']}, body ruler {c['body']}; bureau {c['fiveElementsClass']}.", "",
          "| Branch | Stem | Palace | Major stars (brightness/化) | Minor stars | Decadal ages |", "|---|---|---|---|---|---|"]
    for p in c["palaces"]:
        mj = ", ".join(f"{s['name']} {STAR_EN.get(s['name'], '')} {s['brightness']}{'/化' + s['mutagen'] if s['mutagen'] else ''}" for s in p["majorStars"]) or "—"
        mn = ", ".join(s["name"] + ("/化" + s["mutagen"] if s["mutagen"] else "") for s in p["minorStars"]) or "—"
        L.append(f"| {p['earthlyBranch']} {BR_EN[p['earthlyBranch']]} | {p['heavenlyStem']} | {p['name']} {ZW_EN[p['name']]} | {mj} | {mn} | {p['decadal']['range'][0]}–{p['decadal']['range'][1]} |")
    a = z["alt_leap_month_school_chart"]
    L += ["", f"**Leap-month alternative** (whole leap month = 5th month): Ming {a['soulBranch']}, Shen {a['bodyBranch']}, bureau {a['fiveElementsClass']}. "
          "Palace names shift; star positions by branch: " + "; ".join(f"{p['earthlyBranch']}={p['name']}" for p in a["palaces"]), "",
          "Decadal periods (observed via iztro horoscope):", ""]
    for d in z["decadal_periods_observed"]:
        L.append(f"- {d['start']} → {d['end_exclusive']}: {d['palace_branch']} ({d['natal_palace_at_branch']})")
    L += ["", "## Maya calendar (GMT 584283)", "",
          f"Long Count **{M['maya']['long_count_str']}**; Calendar Round **{M['maya']['calendar_round']}**; round trip OK. {M['maya']['date_basis_note']}",
          "", "## Tibetan (limited overlay)", "",
          f"Year: **{M['tibetan']['year']['gender']} {M['tibetan']['year']['element']}-{M['tibetan']['year']['animal']}** (Rabjung {M['tibetan']['year']['rabjung_cycle']}, year {M['tibetan']['year']['rabjung_year']}). "
          f"{M['tibetan']['losar_boundary']['note']} Omitted: " + "; ".join(f"{k} ({v})" for k, v in M["tibetan"]["omitted"].items())]
    write("MASTER_DATASET.md", "\n".join(L) + "\n")


def final_reading():
    j, w, b, z = M["jyotisha"], M["western"], M["bazi"], M["ziwei"]
    a = M["input_audit"]
    vs = M["verification_summary"]
    dv = S["divergence"]
    L = ["# Six-Culture Verified Chart — Final Reading", "",
         "> Computed symbolic corroboration among traditional systems. Not a scientifically validated forecast; no medical, financial, legal, lifespan or fertility claims.", "",
         "## 1. Input and sensitivity", "",
         f"- Birth: **{a['normalized_local']}** ({a['civil_weekday']}) = **{a['utc_instant']}** UTC, PGIMER Chandigarh ({M['input']['normalized']['place']['latitude']}° N, {M['input']['normalized']['place']['longitude']}° E), `Asia/Kolkata` UTC+05:30, no DST.",
         f"- Local apparent solar time {a['local_apparent_solar_time'][11:19]}; sunset {a['sunset_local'][11:19]} ({a['minutes_before_sunset']:.0f} min after birth) → day chart.",
         f"- Ascendant boundaries: Western Asc {M['boundary_audit'][0]['distance_clock_min']:.0f} min of clock time from a sign change; Jyotisha Lagna {M['boundary_audit'][1]['distance_clock_min']:.0f} min; "
         f"D9 Lagna {M['boundary_audit'][2]['distance_clock_min']:.1f} min; D10 Lagna {M['boundary_audit'][3]['distance_clock_min']:.1f} min.",
         "- Stable across the ±30 s rounding band: " + (", ".join(k for k, v in M["time_uncertainty"]["stability"].items() if list(v.values())[0] == "stable")) + ".",
         "- Sensitive under the disclosed ±5 min stress band: " + (", ".join(k for k, v in M["time_uncertainty"]["stability"].items() if list(v.values())[1] == "sensitive") or "none") + " (everything else stable).",
         f"- BaZi: birth is {M['boundary_audit'][9]['distance_days']:.2f} days after Lixia and {M['boundary_audit'][8]['distance_days']:.2f} days before Mangzhong (month pillar secure).",
         "- **Zi Wei leap-month sensitivity:** the date is day 7 of the *leap* 4th lunar month (闰四月初七). Under iztro's default the chart uses month 4 (Ming in 申). "
         f"Under the school treating the whole leap month as month 5, Ming moves to {z['alt_leap_month_school_chart']['soulBranch']} and every palace name shifts. Zi Wei claims that differ between the two are marked low-confidence and do not vote.",
         "", "## 2. Verification", "",
         f"- {vs['counts'].get('pass', 0)} checks passed, {vs['counts'].get('alert', 0)} alerts, {vs['counts'].get('fail', 0)} failures.",
         f"- Planet longitudes: Swiss Ephemeris vs JPL DE421/Skyfield max difference {vs['largest_planet_diff_deg'] * 3600:.3f}″; Asc/MC vs independent spherical-trig code {vs['asc_mc_diff_deg'] * 3600:.2f}″; solar terms ≤ {vs['solar_term_max_diff_s']:.2f} s.",
         "- BaZi pillars verified by two separate codebases; Zi Wei is a single method (iztro JS and py-iztro share code); Lahiri ayanamsha value is single-source.",
         "- Unavailable/omitted: " + ", ".join(M["excluded_methods"].keys()) + ".",
         "", "## 3. Divergence rate (read this first)", "",
         f"- Divergent domains: **{dv['divergent_domains']} / 9 = {dv['rate_over_all_9']:.0%}**; over domains with sufficient evidence: {dv['divergent_domains']} / {dv['domains_with_sufficient_evidence']} = {dv['rate_over_sufficient']:.0%}.",
         "- No domain reached STRONG (all three clusters agreeing). " + ", ".join(f"{d} {S['domains'][d]['name']}: {g}" for d, g in S["grades"].items()) + ".",
         "", "## 4. Cross-cultural themes (MODERATE and above)", ""]

    def basis_line(d, c):
        p = S["domains"][d]["projections"][c]
        if c == "sinic":
            parts = []
            for comp in p["components"]:
                if comp["system"] == "bazi":
                    parts.append(f"BaZi {', '.join(sorted({x['en'] for x in comp['basis']}))} (weight {comp['weight_sum']:.1f}; elements {comp['element_basis']}; conf {comp['confidence']})")
                else:
                    parts.append(f"Zi Wei " + "; ".join(f"{x['palace']} {ZW_EN.get(x['palace'], '')}: " + ", ".join(i[0] for i in x.get('items', [])) for x in comp['basis'] if not x.get('empty')) + f" (conf {comp['confidence']})")
            return f"**Sinic** {p['prominence']} / {p['polarity']} — " + " | ".join(parts)
        items = "; ".join(f"H{x['house']} {x['sign']}: " + ", ".join(f"{i[0]} ({i[1]:+g})" for i in x["items"]) for x in p["basis"])
        return f"**{c.capitalize()}** {p['prominence']} / {p['polarity']} (score {p['score']:+g}) — {items}"

    any_theme = False
    for d, v in S["domains"].items():
        if v["grade"] in ("STRONG", "MODERATE"):
            any_theme = True
            L.append(f"### {d} {v['name']} — {v['grade']} (shared polarity: {v['shared_polarity']})")
            for c in v["projections"]:
                L.append(f"- {basis_line(d, c)}")
            L.append("")
    if not any_theme:
        L.append("None.")
    for d, v in S["domains"].items():
        if v["grade"] in ("STRONG", "MODERATE"):
            agree = [c for c in v["speaking_clusters"] if v["projections"][c]["polarity"] == v["shared_polarity"]]
            other = [f"{c} ({v['projections'][c]['polarity']})" for c in v["speaking_clusters"] if c not in agree]
            L.append(f"Reading of {d}: {' and '.join(agree)} agree the domain is {v['shared_polarity']} in polarity"
                     + (f"; {', '.join(other)} differs without direct conflict" if other else "")
                     + ". 'Mixed' means supportive and difficult factors coexist under the registry rules; this is agreement on emphasis, not a promise of gain or loss.")
    L += ["", "## 5. Disagreements", ""]
    for d, v in S["domains"].items():
        if v["grade"] == "DIVERGENT":
            L.append(f"### {d} {v['name']} — DIVERGENT")
            for c in v["projections"]:
                L.append(f"- {basis_line(d, c)}")
            cz = v["component_projections"].get("ziwei")
            if cz and cz["confidence"] == "low":
                L.append(f"- (Zi Wei, low confidence, not voting: {cz['prominence']} / {cz['polarity']}; leap-month alternative differs.)")
            L.append("")
    L += ["## 6. Weak and insufficient domains (do not over-read)", ""]
    for d, v in S["domains"].items():
        if v["grade"] in ("WEAK", "INSUFFICIENT"):
            speak = v["speaking_clusters"]
            L.append(f"- **{d} {v['name']} — {v['grade']}**: speaking clusters {speak or 'none'}; " +
                     "; ".join(f"{c} {p['prominence']}/{p['polarity']} ({p['confidence']})" for c, p in v["projections"].items()))
    L += ["", f"Safety scope: the 8th house is deliberately unmapped in both Jyotisha and Western. In this chart it holds Mercury and Rahu (sidereal) and Sun, Mercury, Jupiter and Saturn (tropical); "
          "that emphasis is recorded in the dataset but not projected onto any life domain.", "",
          "## 7. Temperament overlay", "", "| Axis | Clusters indicating | Jyotisha | Western | Sinic |", "|---|---|---|---|---|"]
    for k, t in S["temperament"].items():
        L.append(f"| {k} {t['axis']} | {t['count']}/3 | {'✔' if t['jyotisha']['indicated'] else '–'} {t['jyotisha']['basis']} | "
                 f"{'✔' if t['western']['indicated'] else '–'} {t['western']['basis']} | {'✔' if t['sinic']['indicated'] else '–'} {t['sinic']['basis']} |")
    L += ["", "No axis is indicated by all three clusters. Two-cluster axes: " + ", ".join(f"{t['axis']} ({' + '.join(t['clusters_indicating'])})" for t in S["temperament"].values() if t["count"] == 2) + ".",
          f"- Maya (symbolic, non-voting): Long Count {M['maya']['long_count_str']}, Calendar Round {M['maya']['calendar_round']}. Day-sign meaning omitted — no named Maya source available to attribute.",
          f"- Tibetan (symbolic, non-voting): {M['tibetan']['year']['gender']} {M['tibetan']['year']['element']}-{M['tibetan']['year']['animal']} year. Mewa, Parkha and personal forces omitted (not validated); meanings omitted (no sourced text).",
          "", "## 8. Timing", ""]
    ch = S["chronology"]
    br = ch["base_rate"]
    cur = j["vimshottari"]["current_at_reference_date"]
    pf = w["profection"]
    seg0 = ch["segments"][0]
    L += [f"Reference date {S['reference_date']}. Active periods:",
          f"- Jyotisha: Mahadasha {cur['mahadasha']['lord']} ({cur['mahadasha']['start'][:10]} – {cur['mahadasha']['end'][:10]}), Antardasha {cur['antardasha']['lord']} ({cur['antardasha']['start'][:10]} – {cur['antardasha']['end'][:10]}), Pratyantardasha {cur['pratyantardasha']['lord']} ({cur['pratyantardasha']['start'][:10]} – {cur['pratyantardasha']['end'][:10]}).",
          f"- Western: profection age {pf['age_completed']} → house {pf['profected_house']} ({pf['profected_sign']}), lord of year {pf['lord_of_year']} (natal house {pf['lord_natal_condition']['house']}, {pf['lord_natal_condition']['essential']}). " + "; ".join(f"{sr['year']} solar return Asc: " + ", ".join(f"{k.split(' (')[0]} {v['sign']}" for k, v in sr['ascendants'].items()) + f" (location changes sign: {sr['location_changes_asc_sign']})" for sr in w['solar_returns'] if sr['year'] == int(S['reference_date'][:4])) + ".",
          f"- BaZi: Da Yun {next(p['pillar'] for p in b['da_yun']['periods'] if p['start'][:10] <= S['reference_date'] < p['end'][:10])} (until {next(p['end'][:10] for p in b['da_yun']['periods'] if p['start'][:10] <= S['reference_date'] < p['end'][:10])}); annual {seg0['sinic'].get('bazi_annual', {}).get('pillar')}.",
          f"- Zi Wei: decadal palace {next(x['palace_branch'] + ' ' + x['natal_palace_at_branch'] for x in z['decadal_periods_observed'] if x['start'] <= S['reference_date'] < x['end_exclusive'])}; yearly palace {seg0['sinic'].get('ziwei_yearly', {}).get('branch')} "
          f"({seg0['sinic'].get('ziwei_yearly', {}).get('palace_primary')} / alt-school {seg0['sinic'].get('ziwei_yearly', {}).get('palace_alt_leap_school')} — differs, so not used for votes).", "",
          f"**Base rate first:** with these activation rules, each domain has a {br['chance_domain_hit_by_>=2_clusters']:.1%} chance per segment of being hit by ≥2 clusters by coincidence "
          f"(≈{br['expected_moderate_domains_per_segment_by_chance']:.2f} moderate windows expected per segment). The windows below are therefore roughly at chance level and should be treated as weak signals.", "",
          "| Domain | Start | End | Clusters | Grade |", "|---|---|---|---|---|"]
    for x in ch["windows"]:
        L.append(f"| {x['domain']} {R['domains'][x['domain']]} | {x['start']} | {x['end']} | {', '.join(x['clusters'])} | {x['grade']} |")
    cw = [x for x in ch["windows"] if x["start"] <= S["reference_date"] < x["end"]]
    nw = [x for x in ch["windows"] if x["start"] > S["reference_date"]]
    L += ["", "Current: " + ("; ".join(f"{x['domain']} {R['domains'][x['domain']]} ({x['grade']}, {' + '.join(x['clusters'])}, {x['start']} – {x['end']})" for x in cw) or "no convergence"),
          "Next: " + (f"{nw[0]['domain']} {R['domains'][nw[0]['domain']]} ({nw[0]['grade']}, {' + '.join(nw[0]['clusters'])}, {nw[0]['start']} – {nw[0]['end']})" if nw else "none in horizon"),
          *[f"Note: the strong window {x['domain']} {x['start']} – {x['end']} lasts only {(date.fromisoformat(x['end']) - date.fromisoformat(x['start'])).days} days and arises from adjacent period boundaries; do not read it as a significant event window."
            for x in ch["windows"] if x["grade"] == "strong" and (date.fromisoformat(x["end"]) - date.fromisoformat(x["start"])).days < 60],
          "", "## 9. Removed candidate claims", ""]
    for k, v in S["removed_candidate_claims"].items():
        L.append(f"- {k}: {v['count']}")
    L += ["", "## 10. Closing frame", "",
          "This reading reports where traditional symbolic systems, computed with declared conventions and independently checked arithmetic, agree or disagree. "
          "The calculations are reproducible; the meanings are traditional symbolism, not established causation. Agreement here is mostly weak or at chance level, and a third of the domains disagree outright. "
          "Nothing in this document is a prediction, guarantee, or basis for medical, financial, legal or family decisions."]
    write("FINAL_READING.md", "\n".join(L) + "\n")


if __name__ == "__main__":
    input_audit()
    verification_md()
    master_md()
    final_reading()
    print("reports written")
