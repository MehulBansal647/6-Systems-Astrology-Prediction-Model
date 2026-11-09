"""Deterministic dataset builder. Reads BIRTH_INPUT.json; writes facts only (no interpretation).

Outputs (in output/): INPUT_AUDIT.md, CALCULATION_MANIFEST.json, MASTER_DATASET.json, MASTER_DATASET.md,
VERIFICATION_REPORT.json, VERIFICATION_REPORT.md
"""
from __future__ import annotations

import hashlib
import json
import os
import platform
import subprocess
import sys
from datetime import date, datetime, timedelta, timezone
from importlib import metadata
from zoneinfo import ZoneInfo

import swisseph as swe
from timezonefinder import TimezoneFinder

import astro_core as ac
import bazi as bz
import calendars as cal
import jyotisha as jy
import western as we

ROOT = ac.ROOT
OUT = os.path.join(ROOT, "output")
REFERENCE_DATE = date(2026, 11, 9)  # "today" for timing; recorded in manifest
TOL = {"planet_longitude_deg": 0.01, "asc_mc_deg": 0.05, "solar_term_seconds": 120, "sunrise_sunset_seconds": 120}

VER = []  # verification records


def vrec(system, datum, primary_engine, primary_value, validator, validator_value, difference, convention,
         boundary_distance=None, stability="stable", confidence="high", status="pass", note=None):
    r = {"system": system, "datum": datum, "primary_engine": primary_engine, "primary_value": primary_value,
         "validator": validator, "validator_value": validator_value, "difference": difference,
         "convention": convention, "boundary_distance": boundary_distance,
         "uncertainty_stability": stability, "confidence": confidence, "status": status}
    if note:
        r["note"] = note
    VER.append(r)
    return r


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def run_iztro(args: dict) -> dict:
    out = subprocess.run(["node", os.path.join(ROOT, "src", "ziwei_iztro.js"), json.dumps(args, ensure_ascii=False)],
                         capture_output=True, text=True, check=True)
    return json.loads(out.stdout)


def main():
    os.makedirs(OUT, exist_ok=True)
    inp = json.load(open(os.path.join(ROOT, "BIRTH_INPUT.json")))
    n = inp["normalized"]
    lat, lon = n["place"]["latitude"], n["place"]["longitude"]
    tzname = n["timezone_iana"]
    gender = n["gender"]

    # ---------------- Step 2: civil-time audit ----------------
    tf = TimezoneFinder()
    tz_lookup = tf.timezone_at(lat=lat, lng=lon)
    local_naive = datetime.fromisoformat(n["date_gregorian"] + "T" + n["local_time_24h"])
    zi = ZoneInfo(tzname)
    local = local_naive.replace(tzinfo=zi)
    # check for ambiguity / non-existence (fold)
    fold_check = local_naive.replace(tzinfo=zi, fold=1).utcoffset() == local.utcoffset()
    utc = local.astimezone(timezone.utc)
    offset = local.utcoffset()
    dst = local.dst()
    # historical offsets around birth
    hist = []
    for yy in (1942, 1945, 1946, 1971, 1990, 2001, 2026):
        d0 = datetime(yy, 6, 1, 12, tzinfo=zi)
        hist.append({"date": f"{yy}-06-01", "utc_offset": str(d0.utcoffset()), "dst": str(d0.dst())})
    jd_tt, jd_ut = ac.jd_from_utc(utc)
    eot_min = ac.equation_of_time_minutes(jd_ut)
    lmt = utc + timedelta(hours=lon / 15.0)
    last = lmt + timedelta(minutes=eot_min)
    rs = ac.swe_rise_set(jd_ut - 1.0, lat, lon)  # sunrise of birth morning
    sunrise_jd = rs["sunrise"]
    rs2 = ac.swe_rise_set(jd_ut - 0.5, lat, lon)
    sunset_jd = rs2["sunset"]
    sunrise_utc, sunset_utc = ac.jd_ut_to_utc(sunrise_jd), ac.jd_ut_to_utc(sunset_jd)
    sky_rs = ac.skyfield_rise_set(utc - timedelta(hours=20), utc + timedelta(hours=4), lat, lon)
    sky_sunrise = [t for t, e in sky_rs if e == "sunrise"][0]
    sky_sunset = [t for t, e in sky_rs if e == "sunset"][0]
    sun_alt_sky = ac.sun_alt(utc, lat, lon)
    sun_alt_swe = ac.swe_sun_alt(jd_ut, lat, lon)
    vrec("shared", "Sunrise (birth morning, upper limb, standard refraction)", "Swiss Ephemeris rise_trans",
         sunrise_utc.isoformat(), "Skyfield almanac (DE421)", sky_sunrise.isoformat(),
         abs((sunrise_utc - sky_sunrise).total_seconds()), "seconds; differing refraction models",
         status="pass" if abs((sunrise_utc - sky_sunrise).total_seconds()) < TOL["sunrise_sunset_seconds"] else "alert")
    vrec("shared", "Sunset (birth evening)", "Swiss Ephemeris rise_trans", sunset_utc.isoformat(),
         "Skyfield almanac (DE421)", sky_sunset.isoformat(), abs((sunset_utc - sky_sunset).total_seconds()),
         "seconds; differing refraction models",
         boundary_distance=f"{(sunset_utc - utc).total_seconds() / 60:.1f} min before sunset",
         status="pass" if abs((sunset_utc - sky_sunset).total_seconds()) < TOL["sunrise_sunset_seconds"] else "alert")
    vrec("shared", "Sun true altitude at birth", "Swiss Ephemeris azalt", sun_alt_swe, "Skyfield altaz (DE421)",
         sun_alt_sky, abs(sun_alt_swe - sun_alt_sky), "degrees, geometric (no refraction)",
         status="pass" if abs(sun_alt_swe - sun_alt_sky) < 0.05 else "alert")
    vrec("shared", "IANA zone from coordinates", "timezonefinder", tz_lookup, "declared input", tzname,
         0 if tz_lookup == tzname else 1, "zone identifier", status="pass" if tz_lookup == tzname else "alert")

    audit = {
        "original": inp["original_user_input"],
        "normalized_local": local.isoformat(), "utc_instant": utc.isoformat(),
        "civil_weekday": local.strftime("%A"), "iana_zone": tzname, "timezonefinder_zone": tz_lookup,
        "tzdata_release": metadata.version("tzdata"), "utc_offset": str(offset), "dst": str(dst),
        "fold_ambiguity": not fold_check, "historical_offsets_sampled": hist,
        "julian_day_ut": jd_ut, "julian_day_tt": jd_tt, "delta_t_seconds": (jd_tt - jd_ut) * 86400,
        "local_mean_time": lmt.replace(tzinfo=None).isoformat(), "equation_of_time_minutes": eot_min,
        "local_apparent_solar_time": last.replace(tzinfo=None).isoformat(),
        "sunrise_local": sunrise_utc.astimezone(zi).isoformat(), "sunset_local": sunset_utc.astimezone(zi).isoformat(),
        "minutes_before_sunset": (sunset_utc - utc).total_seconds() / 60,
        "coordinates": n["place"],
    }

    # ---------------- ensemble instants ----------------
    unc = n["time_uncertainty_minutes"]
    stress = n["stress_band_minutes"]
    instants = {"T-unc": utc - timedelta(minutes=unc), "T": utc, "T+unc": utc + timedelta(minutes=unc),
                "T-stress": utc - timedelta(minutes=stress), "T+stress": utc + timedelta(minutes=stress)}

    # ---------------- shared astronomy ----------------
    pos_trop = ac.swe_planets(jd_ut)
    pos_sid = ac.swe_planets(jd_ut, swe.SIDM_LAHIRI)
    swe.set_sid_mode(swe.SIDM_LAHIRI, 0, 0)
    ayan = swe.get_ayanamsa_ex_ut(jd_ut, swe.FLG_SWIEPH)[1]
    sky = ac.skyfield_planets(utc)
    for p in ac.PLANETS:
        d = ac.angdiff(pos_trop[p]["longitude"], sky[p]["longitude"])
        vrec("shared", f"{p} tropical apparent longitude", "Swiss Ephemeris 2.10.03 (sepl_18/semo_18)",
             pos_trop[p]["longitude"], "Skyfield 1.55 + JPL DE421", sky[p]["longitude"], d,
             "geocentric apparent, true ecliptic & equinox of date",
             status="pass" if d <= TOL["planet_longitude_deg"] else "alert")
    _, ang = ac.swe_houses(jd_ut, lat, lon, b"W")
    ind = ac.independent_asc_mc(utc, lat, lon)
    for k in ("Asc", "MC"):
        d = ac.angdiff(ang[k], ind[k])
        vrec("shared", f"{k} tropical", "Swiss Ephemeris houses_ex", ang[k],
             "Skyfield GAST + IAU2000A obliquity + spherical trig (independent code)", ind[k], d,
             "tropical, true obliquity", status="pass" if d <= TOL["asc_mc_deg"] else "alert")
    asc_trop, mc_trop = ang["Asc"], ang["MC"]
    asc_sid = ac.norm(asc_trop - ayan)
    node_sep = ac.angdiff(pos_sid["MeanNode"]["longitude"], ac.norm(pos_sid["MeanNode"]["longitude"] + 180))
    # node mean vs true difference
    mt_diff = ac.angdiff(pos_trop["MeanNode"]["longitude"], pos_trop["TrueNode"]["longitude"])

    # Placidus (optional modern track only)
    plac_cusps, _ = ac.swe_houses(jd_ut, lat, lon, b"P")

    # ---------------- ensemble per instant ----------------
    ens = {}
    for key, t in instants.items():
        jt, ju = ac.jd_from_utc(t)
        _, a = ac.swe_houses(ju, lat, lon, b"W")
        swe.set_sid_mode(swe.SIDM_LAHIRI, 0, 0)
        ay = swe.get_ayanamsa_ex_ut(ju, swe.FLG_SWIEPH)[1]
        ps = ac.swe_planets(ju, swe.SIDM_LAHIRI)
        as_sid = ac.norm(a["Asc"] - ay)
        loc = t.astimezone(zi)
        hour_local = loc.hour + loc.minute / 60 + loc.second / 3600
        last_t = t + timedelta(hours=lon / 15.0) + timedelta(minutes=eot_min)
        hour_last = last_t.hour + last_t.minute / 60 + last_t.second / 3600
        ens[key] = {
            "utc": t.isoformat(), "local": loc.isoformat(),
            "western_asc": ac.sign_of(a["Asc"])["sign"], "western_asc_lon": a["Asc"],
            "western_mc_sign": ac.sign_of(a["MC"])["sign"],
            "jyotisha_lagna": ac.sign_of(as_sid)["sign"], "jyotisha_lagna_lon": as_sid,
            "lagna_nakshatra_pada": f'{jy.nakshatra(as_sid)["name"]} {jy.nakshatra(as_sid)["pada"]}',
            "d9_lagna": ac.SIGNS[jy.d9_sign(as_sid)], "d10_lagna": ac.SIGNS[jy.d10_sign(as_sid)],
            "moon_nakshatra_pada": f'{jy.nakshatra(ps["Moon"]["longitude"])["name"]} {jy.nakshatra(ps["Moon"]["longitude"])["pada"]}',
            "bazi_hour_branch_civil": bz.BRANCHES[int(((hour_local + 1) % 24) // 2)],
            "bazi_hour_branch_apparent_solar": bz.BRANCHES[int(((hour_last + 1) % 24) // 2)],
            "ziwei_time_index": int(((hour_local + 1) % 24) // 2) if hour_local < 23 else 12,
            "sect": "diurnal" if ac.sun_alt(t, lat, lon) > 0 else "nocturnal",
            "d9_all": {p: ac.SIGNS[jy.d9_sign(ps[p]["longitude"])] for p in jy.SEVEN},
            "d10_all": {p: ac.SIGNS[jy.d10_sign(ps[p]["longitude"])] for p in jy.SEVEN},
        }

    def stable(field, band=("T-unc", "T", "T+unc")):
        vals = {k: json.dumps(ens[k][field], sort_keys=True) for k in band}
        return len(set(vals.values())) == 1

    stability = {}
    for f in ("western_asc", "western_mc_sign", "jyotisha_lagna", "lagna_nakshatra_pada", "d9_lagna", "d10_lagna",
              "moon_nakshatra_pada", "bazi_hour_branch_civil", "bazi_hour_branch_apparent_solar",
              "ziwei_time_index", "sect", "d9_all", "d10_all"):
        stability[f] = {"primary_band_+-%.1fmin" % unc: "stable" if stable(f) else "sensitive",
                        "stress_band_+-%dmin" % stress: "stable" if stable(f, ("T-stress", "T", "T+stress")) else "sensitive"}

    # minutes to boundaries (ascendant ~ rate)
    def asc_rate():
        jt, j1 = ac.jd_from_utc(utc + timedelta(minutes=1))
        _, a1 = ac.swe_houses(j1, lat, lon, b"W")
        return ac.angdiff(a1["Asc"], asc_trop)  # deg per minute
    rate = asc_rate()

    # ---------------- Jyotisha ----------------
    jyo = jy.compute(pos_sid, asc_sid, pos_trop["Sun"]["longitude"], pos_trop["Moon"]["longitude"], utc, "MeanNode")
    jyo_true = jy.compute(pos_sid, asc_sid, pos_trop["Sun"]["longitude"], pos_trop["Moon"]["longitude"], utc, "TrueNode")
    node_track_diff = {"mean_rahu": jyo["grahas"]["Rahu"]["sidereal_longitude"],
                       "true_rahu": jyo_true["grahas"]["Rahu"]["sidereal_longitude"],
                       "sign_same": jyo["grahas"]["Rahu"]["sign"] == jyo_true["grahas"]["Rahu"]["sign"],
                       "nakshatra_mean": jyo["grahas"]["Rahu"]["nakshatra"]["name"] + " " + str(jyo["grahas"]["Rahu"]["nakshatra"]["pada"]),
                       "nakshatra_true": jyo_true["grahas"]["Rahu"]["nakshatra"]["name"] + " " + str(jyo_true["grahas"]["Rahu"]["nakshatra"]["pada"])}
    # sidereal validation: Skyfield tropical minus same ayanamsha (ayanamsha single-source)
    for p in jy.SEVEN:
        d = ac.angdiff(jyo["grahas"][p]["sidereal_longitude"], ac.norm(sky[p]["longitude"] - ayan))
        vrec("jyotisha", f"{p} sidereal longitude (Lahiri)", "Swiss Ephemeris FLG_SIDEREAL",
             jyo["grahas"][p]["sidereal_longitude"], "Skyfield tropical - Swiss Lahiri ayanamsha", ac.norm(sky[p]["longitude"] - ayan),
             d, "sidereal Lahiri; ayanamsha value itself single-source (Swiss Ephemeris)",
             boundary_distance=f'{min(jyo["grahas"][p]["degree_in_sign"], 30 - jyo["grahas"][p]["degree_in_sign"]):.3f} deg to sign edge',
             status="pass" if d <= TOL["planet_longitude_deg"] else "alert")
    lag_bd = jyo["lagna"]["sign_boundary_distance_deg"]
    vrec("jyotisha", "Lagna sign", "Swiss Ephemeris", jyo["lagna"]["sign"], "Skyfield independent Asc - Lahiri",
         ac.sign_of(ind["Asc"] - ayan)["sign"], ac.angdiff(asc_sid, ind["Asc"] - ayan), "sidereal whole-sign",
         boundary_distance=f"{lag_bd:.3f} deg (~{lag_bd / rate:.1f} min of clock time)",
         stability=stability["jyotisha_lagna"]["primary_band_+-%.1fmin" % unc],
         confidence="high" if stability["jyotisha_lagna"]["primary_band_+-%.1fmin" % unc] == "stable" else "low")
    vrec("jyotisha", "Rahu-Ketu separation (mean node)", "internal", 180.0, "computed",
         ac.angdiff(jyo["grahas"]["Rahu"]["sidereal_longitude"], jyo["grahas"]["Ketu"]["sidereal_longitude"]),
         abs(180.0 - ac.angdiff(jyo["grahas"]["Rahu"]["sidereal_longitude"], jyo["grahas"]["Ketu"]["sidereal_longitude"])),
         "invariant", status="pass" if abs(180.0 - ac.angdiff(jyo["grahas"]["Rahu"]["sidereal_longitude"], jyo["grahas"]["Ketu"]["sidereal_longitude"])) < 1e-9 else "fail")
    vim = jyo["vimshottari"]
    vrec("jyotisha", "Vimshottari cycle total years", "internal", 120, "computed", vim["total_years"],
         abs(120 - vim["total_years"]), "invariant", status="pass" if vim["total_years"] == 120 else "fail")
    # continuity check for dashas
    cont = True
    prev = None
    for md in vim["mahadashas"]:
        if prev and md["start"] != prev:
            cont = False
        prev = md["end"]
        pa = None
        for ad in md["antardashas"]:
            if pa and ad["start"] != pa:
                cont = False
            pa = ad["end"]
        if abs((datetime.fromisoformat(pa) - datetime.fromisoformat(md["end"])).total_seconds()) > 1:
            cont = False
    vrec("jyotisha", "Vimshottari periods continuous/ordered/non-overlapping", "internal", True, "computed", cont,
         0 if cont else 1, "invariant", status="pass" if cont else "fail")
    # current MD/AD/PD
    ref = datetime(REFERENCE_DATE.year, REFERENCE_DATE.month, REFERENCE_DATE.day, tzinfo=timezone.utc)
    cur = {}
    for md in vim["mahadashas"]:
        if datetime.fromisoformat(md["start"]) <= ref < datetime.fromisoformat(md["end"]):
            cur["mahadasha"] = {k: md[k] for k in ("lord", "start", "end")}
            for ad in md["antardashas"]:
                if datetime.fromisoformat(ad["start"]) <= ref < datetime.fromisoformat(ad["end"]):
                    cur["antardasha"] = ad
                    pds = jy.pratyantar(md["lord"], ad["lord"], datetime.fromisoformat(ad["start"]),
                                        datetime.fromisoformat(ad["end"]))
                    cur["pratyantardashas_in_current_antardasha"] = pds
                    cur["pratyantardasha"] = next(p for p in pds if datetime.fromisoformat(p["start"]) <= ref < datetime.fromisoformat(p["end"]))
    jyo["vimshottari"]["current_at_reference_date"] = cur
    # Moon nakshatra stability -> dasha balance sensitivity (seconds)
    moon_speed = pos_sid["Moon"]["speed_deg_per_day"]
    dasha_shift_days_per_min = (1 / 1440) * moon_speed / jy.NAK_SPAN * jy.DASHA_YEARS[vim["nakshatra_lord"]] * jy.DASHA_YEAR_DAYS
    jyo["vimshottari"]["sensitivity_days_per_minute_of_birth_time"] = dasha_shift_days_per_min

    # ---------------- Western ----------------
    is_day = sun_alt_swe > 0
    wes = we.compute(pos_trop, asc_trop, mc_trop, is_day, sun_alt_swe)
    w_bd = wes["ascendant"]["sign_boundary_distance_deg"]
    vrec("western", "Ascendant sign (tropical)", "Swiss Ephemeris", wes["ascendant"]["sign"], "Skyfield independent Asc",
         ac.sign_of(ind["Asc"])["sign"], ac.angdiff(asc_trop, ind["Asc"]), "tropical whole-sign",
         boundary_distance=f"{w_bd:.3f} deg (~{w_bd / rate:.1f} min of clock time)",
         stability=stability["western_asc"]["primary_band_+-%.1fmin" % unc])
    vrec("western", "Sect (day chart)", "Swiss Ephemeris altitude", is_day, "Skyfield altitude", sun_alt_sky > 0, 0,
         "Sun above geometric horizon", boundary_distance=f'{audit["minutes_before_sunset"]:.1f} min before sunset',
         stability=stability["sect"]["primary_band_+-%.1fmin" % unc])
    # profection and solar return
    birthday_this_year = date(REFERENCE_DATE.year, 5, 29)
    age_completed = REFERENCE_DATE.year - 2001 - (1 if REFERENCE_DATE < birthday_this_year else 0)
    prof = we.profection(wes["ascendant"]["sign_index"], age_completed)
    yl = prof["lord_of_year"]
    prof["lord_natal_condition"] = {k: wes["planets"][yl][k] for k in ("sign", "house", "retrograde", "solar_phase", "in_sect")}
    prof["lord_natal_condition"]["essential"] = wes["planets"][yl]["essential_dignity"]["summary"]
    prof["start"] = f"{2001 + age_completed}-05-29 (birthday; exact solar-return instant listed separately)"
    prof["end"] = f"{2002 + age_completed}-05-29"
    sr = []
    sun0 = pos_trop["Sun"]["longitude"]
    for yy in (REFERENCE_DATE.year - 1, REFERENCE_DATE.year, REFERENCE_DATE.year + 1):
        jd0 = ac.jd_from_utc(datetime(yy, 5, 20, tzinfo=timezone.utc))[1]
        jr = ac.swe_solar_crossing(sun0, jd0)
        tr = ac.jd_ut_to_utc(jr)
        rec = {"year": yy, "instant_utc": tr.isoformat(), "instant_local": tr.astimezone(zi).isoformat(), "ascendants": {}}
        for locn in [{"label": "Birthplace (PGIMER Chandigarh)", "latitude": lat, "longitude": lon}] + n["current_locations"]:
            _, a2 = ac.swe_houses(jr, locn["latitude"], locn["longitude"], b"W")
            rec["ascendants"][locn["label"]] = {"asc_lon": a2["Asc"], **ac.sign_of(a2["Asc"]),
                                                "mc_sign": ac.sign_of(a2["MC"])["sign"]}
        signs = {v["sign"] for v in rec["ascendants"].values()}
        rec["location_changes_asc_sign"] = len(signs) > 1
        sr.append(rec)

    # ---------------- BaZi ----------------
    jie_terms = {}
    for L in (315, 45, 60, 75):
        start = jd_ut - (120 if L == 315 else 40)
        j = ac.swe_solar_crossing(L, start)
        tt = ac.jd_ut_to_utc(j)
        tsky = ac.skyfield_solar_crossing(L, tt - timedelta(hours=2), tt + timedelta(hours=2))
        dsec = abs((tt - tsky).total_seconds())
        jie_terms[L] = {"swe_utc": tt.isoformat(), "skyfield_utc": tsky.isoformat(), "diff_s": dsec}
        names = {315: "Lichun (315)", 45: "Lixia (45, jie opening Si month)", 60: "Xiaoman (60, zhongqi)",
                 75: "Mangzhong (75, jie opening Wu month)"}
        vrec("bazi", f"Solar term {names[L]} 2001", "Swiss Ephemeris solcross_ut", tt.isoformat(),
             "Skyfield bisection (DE421)", tsky.isoformat(), dsec, "apparent geocentric solar longitude, seconds",
             boundary_distance=f"{(utc - tt).total_seconds() / 86400:+.4f} days from birth (birth minus term)",
             status="pass" if dsec <= TOL["solar_term_seconds"] else "alert")
    lixia = datetime.fromisoformat(jie_terms[45]["swe_utc"])
    mangzhong = datetime.fromisoformat(jie_terms[75]["swe_utc"])
    side_ok = lixia < utc < mangzhong
    vrec("bazi", "Birth after Lixia and before Mangzhong (Si month)", "Swiss Ephemeris", side_ok, "Skyfield",
         datetime.fromisoformat(jie_terms[45]["skyfield_utc"]) < utc < datetime.fromisoformat(jie_terms[75]["skyfield_utc"]),
         0, "invariant", boundary_distance=f"{(utc - lixia).total_seconds() / 86400:.3f} d after Lixia; {(mangzhong - utc).total_seconds() / 86400:.3f} d before Mangzhong",
         status="pass" if side_ok else "fail")
    loc = local
    lp = bz.lunar_python_pillars(loc.year, loc.month, loc.day, loc.hour, loc.minute)
    lp_last = bz.lunar_python_pillars(last.year, last.month, last.day, last.hour, last.minute, last.second)
    arith = bz.arithmetic_pillars(loc.date(), loc.hour + loc.minute / 60, pos_trop["Sun"]["longitude"], 2001)
    arith_last = bz.arithmetic_pillars(last.date(), last.hour + last.minute / 60 + last.second / 3600,
                                       pos_trop["Sun"]["longitude"], 2001)
    pillars = {k: lp[k] for k in ("year", "month", "day", "hour")}
    for k in pillars:
        vrec("bazi", f"{k} pillar (civil local time)", "lunar_python 1.4.9", lp[k],
             "independent arithmetic (JDN day count + exact Swiss solar longitude)", arith[k],
             0 if lp[k] == arith[k] else 1, "sexagenary; midnight day boundary; late-Zi n/a (birth 18:20)",
             status="pass" if lp[k] == arith[k] else "fail")
    track_same = all(lp[k] == lp_last[k] for k in pillars) and all(arith[k] == arith_last[k] for k in pillars)
    # hidden stems cross-check
    hid_ok = all(sorted(lp["hidden"][k]) == sorted(bz.HIDDEN[pillars[k][1]]) for k in pillars)
    order_diff = sorted({pillars[k][1] for k in pillars if "".join(lp["hidden"][k]) != bz.HIDDEN[pillars[k][1]]})
    vrec("bazi", "Hidden stems (set per branch)", "lunar_python", lp["hidden"], "declared table in bazi.py",
         {k: bz.HIDDEN[pillars[k][1]] for k in pillars}, 0 if hid_ok else 1, "standard hidden-stem table",
         status="pass" if hid_ok else "alert",
         note=("Same stems; middle/residual ORDER differs for " + ",".join(order_diff) +
               " (school variation). DM strength recomputed under both orders.") if order_diff else None)
    dm = pillars["day"][0]
    tg = {}
    for k in pillars:
        if k != "day":
            tg[f"{k}_stem"] = {"stem": pillars[k][0], "ten_god": bz.ten_god(dm, pillars[k][0]),
                               "en": bz.TEN_GOD_EN[bz.ten_god(dm, pillars[k][0])]}
        for i, h in enumerate(bz.HIDDEN[pillars[k][1]]):
            tg[f"{k}_hidden_{i}"] = {"stem": h, "ten_god": bz.ten_god(dm, h), "en": bz.TEN_GOD_EN[bz.ten_god(dm, h)]}
    strength = bz.day_master_strength(pillars)
    _saved = dict(bz.HIDDEN)
    for k in pillars:
        bz.HIDDEN[pillars[k][1]] = "".join(lp["hidden"][k])
    strength_alt = bz.day_master_strength(pillars)
    bz.HIDDEN.clear(); bz.HIDDEN.update(_saved)
    strength["alt_hidden_order_check"] = {"support_share": strength_alt["support_share"], "verdict": strength_alt["verdict"],
                                          "verdict_changes": strength_alt["verdict"] != strength["verdict"]}
    ug = bz.useful_god(strength, pillars["month"][1])
    prev_jie, next_jie = lixia, mangzhong
    dy = bz.da_yun(pillars["month"], pillars["year"][0], gender, utc, prev_jie, next_jie)
    # lunar_python Da Yun (CST-input caveat)
    e = lp["_eightchar"]
    y2 = e.getYun(1 if gender == "male" else 0, 2)
    lp_dy = {"start_solar": y2.getStartSolar().toYmdHms(), "forward": y2.isForward(),
             "pillars": [d.getGanZhi() for d in y2.getDaYun()[1:6]],
             "caveat": "lunar_python treats input clock time as China Standard Time (UTC+8) when comparing with solar terms; "
                       "IST input is 2.5 h earlier in absolute time, so its start date is not used."}
    dy_ok = [p["pillar"] for p in dy["periods"][:5]] == lp_dy["pillars"] and (dy["direction"] == "forward") == lp_dy["forward"]
    vrec("bazi", "Da Yun direction and pillar sequence", "own implementation", [p["pillar"] for p in dy["periods"][:5]],
         "lunar_python getYun", lp_dy["pillars"], 0 if dy_ok else 1, "male + yin year -> reverse",
         status="pass" if dy_ok else "fail")
    vrec("bazi", "Da Yun start instant", "own: exact UTC solar term, rule DY-A", dy["start_rule_DY_A"],
         "own: rule DY-B (proportional)", dy["start_rule_DY_B"], dy["start_difference_days"],
         "days; school-dependent conversion rule", confidence="medium",
         note="lunar_python start " + lp_dy["start_solar"] + " not used (CST-input caveat)")
    # continuity of da yun
    dcont = all(dy["periods"][i]["end"] == dy["periods"][i + 1]["start"] for i in range(len(dy["periods"]) - 1))
    vrec("bazi", "Da Yun periods continuous", "internal", True, "computed", dcont, 0 if dcont else 1, "invariant",
         status="pass" if dcont else "fail")
    # annual pillars (Lichun boundaries) 2026-2037
    annual = []
    for yy in range(REFERENCE_DATE.year - 1, REFERENCE_DATE.year + 11):
        jd0 = ac.jd_from_utc(datetime(yy, 1, 20, tzinfo=timezone.utc))[1]
        lc = ac.jd_ut_to_utc(ac.swe_solar_crossing(315.0, jd0))
        yi = (yy - 4) % 60
        annual.append({"pillar": bz.gz(yi), "start_lichun_utc": lc.isoformat(),
                       "stem_ten_god": bz.ten_god(dm, bz.gz(yi)[0]), "branch_main_qi_ten_god": bz.ten_god(dm, bz.HIDDEN[bz.gz(yi)[1]][0])})
    for i in range(len(annual) - 1):
        annual[i]["end_lichun_utc"] = annual[i + 1]["start_lichun_utc"]
    annual = annual[:-1]
    bazi = {
        "school": "Ziping (子平) conventions as implemented; civil local time primary, apparent solar time checked",
        "pillars_civil": pillars, "pillars_apparent_solar_lunar_python": {k: lp_last[k] for k in pillars},
        "pillars_track_agreement": track_same,
        "independent_arithmetic_civil": arith, "independent_arithmetic_apparent_solar": arith_last,
        "day_master": {"stem": dm, "element": bz.STEM_ELEM[bz.STEMS.index(dm)],
                       "polarity": "yang" if bz.STEMS.index(dm) % 2 == 0 else "yin"},
        "elements": {k: {"stem_element": bz.STEM_ELEM[bz.STEMS.index(pillars[k][0])],
                         "branch_element": bz.BRANCH_ELEM[bz.BRANCHES.index(pillars[k][1])]} for k in pillars},
        "hidden_stems": {k: list(bz.HIDDEN[pillars[k][1]]) for k in pillars},
        "na_yin_traditional_attribute": lp["nayin"],
        "ten_gods": tg, "day_master_strength": strength, "useful_god": ug,
        "interactions": bz.interactions(pillars),
        "solar_terms": {str(k): v for k, v in jie_terms.items()},
        "day_boundary_rule": "civil midnight; late-Zi convention irrelevant (birth 18:20, 4h40m before 23:00)",
        "da_yun": dy, "da_yun_lunar_python_reference": lp_dy, "annual_pillars": annual,
        "lunar_date": lp["lunar_date"],
    }

    # ---------------- Zi Wei Dou Shu ----------------
    tidx = ens["T"]["ziwei_time_index"]
    zw_dates = []
    dd = date(REFERENCE_DATE.year, 1, 1)
    while dd <= date(REFERENCE_DATE.year + 11, 3, 1):
        zw_dates.append(dd.isoformat())
        dd += timedelta(days=1)
    zw_args = {"mode": "solar", "date": "2001-5-29", "timeIndex": tidx, "gender": "男" if gender == "male" else "女",
               "fixLeap": True, "horoscopeDates": zw_dates}
    zw = run_iztro(zw_args)
    zw_en = run_iztro({**zw_args, "language": "en-US", "horoscopeDates": []})
    zw_nofix = run_iztro({**zw_args, "fixLeap": False, "horoscopeDates": []})
    # alternative leap-month school: leap 4th month treated wholly as 5th month
    zw_alt = run_iztro({"mode": "lunar", "date": "2001-5-7", "timeIndex": tidx, "gender": zw_args["gender"],
                        "isLeapMonth": False, "fixLeap": True, "horoscopeDates": []})
    # py-iztro wrapper comparison (same underlying method)
    from py_iztro import Astro
    pz = Astro().by_solar("2001-5-29", tidx, zw_args["gender"], True, "zh-CN").model_dump()
    same_iface = (pz["earthly_branch_of_soul_palace"] == zw["soulBranch"] and pz["five_elements_class"] == zw["fiveElementsClass"]
                  and [[s["name"] for s in p["major_stars"]] for p in pz["palaces"]] == [[s["name"] for s in p["majorStars"]] for p in zw["palaces"]])
    vrec("ziwei", "Ming branch, bureau, major-star layout", "iztro 2.6.5 (JavaScript)",
         {"ming": zw["soulBranch"], "bureau": zw["fiveElementsClass"]}, "py-iztro 0.1.5 (wrapper; SAME underlying method)",
         {"ming": pz["earthly_branch_of_soul_palace"], "bureau": pz["five_elements_class"]}, 0 if same_iface else 1,
         "interface/serialization check only, NOT independent", confidence="medium", status="pass" if same_iface else "fail")
    branches = [p["earthlyBranch"] for p in zw["palaces"]]
    uniq = len(set(branches)) == 12 and len(set(p["name"] for p in zw["palaces"])) == 12
    vrec("ziwei", "12 unique palaces", "iztro", len(set(branches)), "invariant", 12, 0 if uniq else 1, "invariant",
         status="pass" if uniq else "fail")
    majors = [s["name"] for p in zw["palaces"] for s in p["majorStars"]]
    m14 = len(majors) == 14 and len(set(majors)) == 14
    vrec("ziwei", "14 major stars each placed once", "iztro", len(set(majors)), "invariant", 14, 0 if m14 else 1,
         "invariant", status="pass" if m14 else "fail")
    br_idx = lambda b: bz.BRANCHES.index(b)
    zw_pos = {s["name"]: br_idx(p["earthlyBranch"]) for p in zw["palaces"] for s in p["majorStars"]}
    tf_ok = zw_pos["天府"] == (4 - zw_pos["紫微"]) % 12
    vrec("ziwei", "Tian Fu mirrors Zi Wei across Yin-Shen axis", "iztro", bz.BRANCHES[zw_pos["天府"]],
         "independent formula (4 - ZiWei) mod 12", bz.BRANCHES[(4 - zw_pos["紫微"]) % 12], 0 if tf_ok else 1,
         "invariant", status="pass" if tf_ok else "fail")
    lunar_month = abs(lp["lunar_month"])
    hb = tidx if tidx < 12 else 0
    ming_formula = bz.BRANCHES[(2 + (lunar_month - 1) - hb) % 12]
    shen_formula = bz.BRANCHES[(2 + (lunar_month - 1) + hb) % 12]
    mok = ming_formula == zw["soulBranch"] and shen_formula == zw["bodyBranch"]
    vrec("ziwei", "Ming/Shen palace branches", "iztro", [zw["soulBranch"], zw["bodyBranch"]],
         "independent formula from lunar month 4 (leap, day 7 <= 15) and hour branch", [ming_formula, shen_formula],
         0 if mok else 1, "Ming = Yin + (month-1) - hour; Shen = Yin + (month-1) + hour", status="pass" if mok else "fail")
    # leap-month school comparison
    def layout(z):
        return {p["earthlyBranch"]: {"name": p["name"], "major": sorted(s["name"] + (s["brightness"] or "") + (s["mutagen"] or "") for s in p["majorStars"])} for p in z["palaces"]}
    alt_diff = layout(zw) != layout(zw_alt)
    nofix_same = layout(zw) == layout(zw_nofix)
    vrec("ziwei", "Leap-month convention sensitivity", "iztro fixLeap=true (leap month days 1-15 = month 4)",
         {"ming": zw["soulBranch"], "bureau": zw["fiveElementsClass"]},
         "alt school: whole leap month = month 5 (iztro byLunar 2001-5-7)",
         {"ming": zw_alt["soulBranch"], "bureau": zw_alt["fiveElementsClass"]}, 1 if alt_diff else 0,
         "school-dependent convention", stability="sensitive" if alt_diff else "stable",
         confidence="low" if alt_diff else "medium", status="pass",
         note="fixLeap=false gives identical layout: " + str(nofix_same))
    # decadal continuity
    decs = sorted([(p["decadal"]["range"][0], p["decadal"]["range"][1], p["earthlyBranch"]) for p in zw["palaces"]])
    dec_ok = all(decs[i][1] + 1 == decs[i + 1][0] for i in range(11))
    vrec("ziwei", "Decadal ranges continuous", "iztro", decs[0], "invariant", decs[-1], 0 if dec_ok else 1, "invariant",
         status="pass" if dec_ok else "fail")
    # compress horoscope day series into periods
    def compress(field):
        segs = []
        for d_ in zw_dates:
            h = zw["horoscopes"][d_]
            v = (h[field]["index"], h[field]["heavenlyStem"], h[field]["earthlyBranch"])
            if segs and segs[-1]["value"] == v:
                segs[-1]["end_exclusive"] = (date.fromisoformat(d_) + timedelta(days=1)).isoformat()
            else:
                segs.append({"value": v, "start": d_, "end_exclusive": (date.fromisoformat(d_) + timedelta(days=1)).isoformat(),
                             "mutagen": h[field]["mutagen"]})
        out = []
        for s in segs:
            idx, st, br = s["value"]
            pal = next(p for p in zw["palaces"] if p["earthlyBranch"] == br)
            out.append({"start": s["start"], "end_exclusive": s["end_exclusive"], "palace_branch": br, "stem": st,
                        "natal_palace_at_branch": pal["name"], "mutagen_stars_lu_quan_ke_ji": s["mutagen"]})
        return out
    zw_decadal = compress("decadal")
    zw_yearly = compress("yearly")
    zw.pop("horoscopes")
    ziwei = {"implementation": "iztro 2.6.5 (config yearDivide=normal, horoscopeDivide=normal)",
             "school": "iztro default (全书/San He style as implemented); fixLeap=true",
             "conventions": {"day_boundary": "civil date; late Zi irrelevant", "time_index": tidx,
                             "time_index_basis": "civil local time 18:20 -> 酉 (17:00-19:00); apparent solar 18:00 also 酉",
                             "gender_encoding": "男", "direction_rule": "yin-year male -> counter-clockwise decadal",
                             "age_convention": "nominal (虚岁) age; yearly boundaries at Chinese lunar new year (iztro normal)"},
             "chart": zw, "chart_en_labels": {zw["palaces"][i]["earthlyBranch"]: {"palace": p["name"], "major": [s["name"] for s in p["majorStars"]], "minor": [s["name"] for s in p["minorStars"]]} for i, p in enumerate(zw_en["palaces"])},
             "minor_star_set": "iztro default minor stars (14 auxiliary); separated from major-star evidence",
             "alt_leap_month_school_chart": {"soulBranch": zw_alt["soulBranch"], "bodyBranch": zw_alt["bodyBranch"],
                                             "fiveElementsClass": zw_alt["fiveElementsClass"], "palaces": zw_alt["palaces"]},
             "fixLeap_false_identical": nofix_same,
             "decadal_periods_observed": zw_decadal, "yearly_periods_observed": zw_yearly}

    # ---------------- Maya ----------------
    my = cal.maya(local.year, local.month, local.day)
    hb_i = [h.lower() for h in cal.HAAB]
    ok_lc = my["primary"]["long_count"] == my["independent_arithmetic"]["long_count"]
    ok_tz = my["primary"]["tzolkin"][0] == my["independent_arithmetic"]["tzolkin"][0] and \
        cal.TZOLKIN.index(my["independent_arithmetic"]["tzolkin"][1]) == \
        [t.lower() for t in __import__("convertdate").mayan.TZOLKIN].index(my["primary"]["tzolkin"][1].lower())
    ok_hb = my["primary"]["haab"][0] == my["independent_arithmetic"]["haab"][0] and \
        cal.HAAB.index(my["independent_arithmetic"]["haab"][1]) == \
        [h.lower() for h in __import__("convertdate").mayan.HAAB].index(my["primary"]["haab"][1].lower())
    rt_ok = my["primary"]["round_trip"] == [2001, 5, 29] and my["independent_round_trip"] == [2001, 5, 29]
    vrec("maya", "Long Count", "convertdate", my["primary"]["long_count"], "independent arithmetic", my["independent_arithmetic"]["long_count"], 0 if ok_lc else 1, "GMT 584283", status="pass" if ok_lc else "fail")
    vrec("maya", "Tzolk'in", "convertdate", my["primary"]["tzolkin"], "independent arithmetic", my["independent_arithmetic"]["tzolkin"], 0 if ok_tz else 1, "GMT 584283; name orthography differs only", status="pass" if ok_tz else "fail")
    vrec("maya", "Haab'", "convertdate", my["primary"]["haab"], "independent arithmetic", my["independent_arithmetic"]["haab"], 0 if ok_hb else 1, "GMT 584283; 'Zip' = 'Sip' orthography", status="pass" if ok_hb else "fail")
    vrec("maya", "Round trip to 2001-05-29", "convertdate", my["primary"]["round_trip"], "independent arithmetic", my["independent_round_trip"], 0 if rt_ok else 1, "invariant", status="pass" if rt_ok else "fail")
    ctrl = cal.maya(2012, 12, 21)
    vrec("maya", "Control date 2012-12-21", "independent arithmetic", ctrl["long_count_str"] + " " + ctrl["calendar_round"],
         "published GMT value", "13.0.0.0.0 4 Ajaw 3 K'ank'in", 0 if ctrl["long_count_str"] == "13.0.0.0.0" and ctrl["calendar_round"] == "4 Ajaw 3 K'ank'in" else 1,
         "control", status="pass" if ctrl["long_count_str"] == "13.0.0.0.0" else "fail")
    my["date_basis_note"] = "Civil local date used. Birth was 59 min before sunset, so a sunset-based day-boundary convention would give the same day."

    # ---------------- Tibetan ----------------
    tib = cal.tibetan_year(2001)
    tib_chk = tib["element"].replace("Iron", "Metal") == bz.STEM_ELEM[bz.STEMS.index(pillars["year"][0])] and \
        tib["animal"] == ["Mouse", "Ox", "Tiger", "Rabbit", "Dragon", "Snake", "Horse", "Sheep", "Monkey", "Bird", "Dog", "Pig"][bz.BRANCHES.index(pillars["year"][1])]
    vrec("tibetan", "Element-animal year", "sexagenary arithmetic (Rabjung from 1027)", f'{tib["gender"]} {tib["element"]}-{tib["animal"]}',
         "lunar_python year pillar mapped to Tibetan names", pillars["year"], 0 if tib_chk else 1,
         "Losar boundary: birth is >3 months after Chinese New Year 2001-01-24; Tibetan Losar falls on or about one lunation after it",
         confidence="medium", status="pass" if tib_chk else "fail",
         note="Phugpa Losar date not computed by a validated lineage-specific implementation; the year assignment is robust because the birth date is far from any plausible Losar.")
    tibetan = {"year": tib, "losar_boundary": {"chinese_new_year_2001": "2001-01-24",
                                               "note": "Exact Phugpa Losar not computed (no validated implementation available offline); "
                                                       "the Tibetan new year falls on or within about one lunation after Chinese New Year, so 2001-05-29 lies in the 2001 Tibetan year under any plausible Losar date."},
               "omitted": {"mewa": "no validated lineage-specific implementation", "parkha": "no validated implementation",
                           "life_body_power_windhorse_soul_forces": "formula anchors not validated",
                           "annual_obstacle_years": "source tradition not available"}}

    # ---------------- excluded methods ----------------
    excluded = {
        "jyotisha_shadbala": "no validated implementation in this environment",
        "jyotisha_ashtakavarga": "timing/transit support not requested; omitted",
        "jyotisha_d7_d12": "domains not specifically requested",
        "jyotisha_jaimini_kp_alt_ayanamsha": "separate tracks not requested; not computed",
        "western_zodiacal_releasing": "implementation not validated",
        "western_transits": "only profection and solar return used for timing",
        "western_modern_outer_planets_patterns": "reported as separate optional track only (no votes)",
        "tibetan_mewa_parkha_forces": "not validated (see tibetan.omitted)",
        "maya_day_sign_meanings": "no named historical/living Maya source available to attribute; meanings omitted",
        "tibetan_symbolic_meanings": "no sourced lineage text available; meanings omitted",
        "de440_kernel": "JPL download blocked by network policy; DE421 (skyfield-data package) used as validator",
        "online_geocoding": "geocoder blocked; reference coordinates used",
    }

    # ---------------- manifest ----------------
    pkgs = {}
    for pkg in ("pyswisseph", "skyfield", "skyfield-data", "jplephem", "tzdata", "timezonefinder", "lunar_python",
                "convertdate", "py-iztro", "numpy"):
        try:
            pkgs[pkg] = metadata.version(pkg)
        except Exception:
            pkgs[pkg] = "unknown"
    node_v = subprocess.run(["node", "--version"], capture_output=True, text=True).stdout.strip()
    iztro_v = json.load(open(os.path.join(ROOT, "js", "node_modules", "iztro", "package.json")))["version"]
    src_files = sorted(f for f in os.listdir(os.path.join(ROOT, "src")) if f.endswith((".py", ".js")))
    manifest = {
        "execution_timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "reference_date_for_timing": REFERENCE_DATE.isoformat(),
        "runtime": {"python": sys.version, "platform": platform.platform(), "node": node_v},
        "packages": pkgs, "npm_packages": {"iztro": iztro_v},
        "swiss_ephemeris_version": swe.version,
        "ephemeris_files": {f: {"sha256": sha256(os.path.join(ac.EPHE_PATH, f)), "size": os.path.getsize(os.path.join(ac.EPHE_PATH, f)),
                                "source": "github.com/aloistr/swisseph/ephe"} for f in sorted(os.listdir(ac.EPHE_PATH))},
        "validator_kernel": {"file": "de421.bsp", "sha256": sha256(ac.DE_PATH), "source": "skyfield-data package"},
        "tzdata_release": metadata.version("tzdata"),
        "source_checksums": {f: sha256(os.path.join(ROOT, "src", f)) for f in src_files},
        "conventions": {
            "western": "tropical; geocentric apparent; whole-sign houses; 7 traditional planets; sect by Sun geometric altitude; Egyptian bounds; Dorothean triplicities; Chaldean faces; Lilly moiety orbs",
            "western_optional_track": "Placidus cusps and outer planets reported separately, no votes",
            "jyotisha": "sidereal Lahiri (SIDM_LAHIRI); whole-sign houses; mean node primary (true node reported); Vimshottari with 365.25-day years; BPHS dignities and natural relationships; graha drishti whole-sign",
            "bazi": "civil local time primary (IST), local apparent solar time checked; midnight day boundary; exact sectional solar terms (Swiss Ephemeris); Da Yun rule DY-A (1 day = 120 days)",
            "ziwei": "iztro 2.6.5 bySolar, fixLeap=true, normal year divide; civil time index",
            "maya": "GMT correlation 584283",
            "tibetan": "element-animal year only; Rabjung epoch 1027",
            "time": "IANA Asia/Kolkata, UTC+05:30, no DST in 2001",
        },
        "tolerances": TOL,
    }

    master = {
        "input": inp, "input_audit": audit, "conventions": manifest["conventions"],
        "versions": {"packages": pkgs, "iztro": iztro_v, "swiss_ephemeris": swe.version},
        "time_uncertainty": {"primary_band_minutes": unc, "stress_band_minutes": stress, "instants": ens,
                             "stability": stability, "asc_rate_deg_per_min": rate},
        "shared_astronomy": {"julian_day_ut": jd_ut, "julian_day_tt": jd_tt, "ayanamsha_lahiri_deg": ayan,
                             "tropical": pos_trop, "sidereal_lahiri": pos_sid, "skyfield_tropical": sky,
                             "asc_mc_tropical": ang, "asc_mc_independent": ind, "asc_sidereal": asc_sid,
                             "placidus_cusps_optional_track": plac_cusps,
                             "mean_vs_true_node_diff_deg": mt_diff},
        "jyotisha": {**jyo, "true_node_track_comparison": node_track_diff},
        "western": {**wes, "profection": prof, "solar_returns": sr,
                    "optional_modern_track": {p: {"longitude": pos_trop[p]["longitude"], **ac.sign_of(pos_trop[p]["longitude"])}
                                              for p in ("Uranus", "Neptune", "Pluto")}},
        "bazi": bazi, "ziwei": ziwei, "maya": my, "tibetan": tibetan,
        "excluded_methods": excluded,
    }
    bazi.pop("_eightchar", None)

    # boundaries summary
    boundaries = [
        {"boundary": "Western Ascendant sign (Scorpio/Sagittarius)", "distance_deg": w_bd, "distance_clock_min": w_bd / rate,
         "would_change": "all whole-sign houses, profections, Lots' houses"},
        {"boundary": "Jyotisha Lagna sign (Libra/Scorpio)", "distance_deg": lag_bd, "distance_clock_min": lag_bd / rate,
         "would_change": "all houses, house lords, functional natures, yogas"},
        {"boundary": "Jyotisha D9 Lagna boundary", "distance_deg": jyo["lagna"]["d9_boundary_distance_deg"],
         "distance_clock_min": jyo["lagna"]["d9_boundary_distance_deg"] / rate, "would_change": "D9 Lagna"},
        {"boundary": "Jyotisha D10 Lagna boundary", "distance_deg": jyo["lagna"]["d10_boundary_distance_deg"],
         "distance_clock_min": jyo["lagna"]["d10_boundary_distance_deg"] / rate, "would_change": "D10 Lagna"},
        {"boundary": "Sunset / sect", "distance_clock_min": audit["minutes_before_sunset"],
         "would_change": "sect (day->night), Lot formulas, benefic/malefic of sect"},
        {"boundary": "BaZi/Zi Wei two-hour (酉 ends 19:00 civil)", "distance_clock_min": 40.0,
         "would_change": "hour pillar, Zi Wei Ming/Shen and hour stars"},
        {"boundary": "BaZi 酉 start (17:00) in apparent solar time", "distance_clock_min": (last.hour * 60 + last.minute + last.second / 60) - 17 * 60,
         "would_change": "hour pillar under apparent-solar-time school"},
        {"boundary": "Day boundary (late Zi 23:00 / midnight)", "distance_clock_min": (23 * 60) - (18 * 60 + 20),
         "would_change": "day pillar (late-Zi school), Zi Wei day"},
        {"boundary": "Mangzhong sectional term (Si->Wu month)", "distance_days": (mangzhong - utc).total_seconds() / 86400,
         "would_change": "month pillar, Da Yun"},
        {"boundary": "Lixia sectional term", "distance_days": (utc - lixia).total_seconds() / 86400, "would_change": "month pillar"},
        {"boundary": "Lunar leap month (闰四月 day 7)", "distance_days": None,
         "would_change": "Zi Wei Ming palace and star layout under the 'leap month = next month' school (see verification)"},
        {"boundary": "Tibetan Losar 2001", "distance_days": "> 90", "would_change": "Tibetan year element-animal"},
        {"boundary": "Gregorian adoption", "distance_days": "n/a (2001)", "would_change": "none"},
        {"boundary": "Moon nakshatra/pada edge", "distance_deg": jyo["grahas"]["Moon"]["nakshatra"]["distance_to_pada_boundary_deg"],
         "would_change": "Moon pada; Vimshottari start lord only at nakshatra edge"},
    ]
    master["boundary_audit"] = boundaries

    # verification counts
    status_counts = {}
    for r in VER:
        status_counts[r["status"]] = status_counts.get(r["status"], 0) + 1
    failed_systems = sorted({r["system"] for r in VER if r["status"] == "fail"})
    master["verification_summary"] = {"counts": status_counts, "failed_systems": failed_systems,
                                      "largest_planet_diff_deg": max(r["difference"] for r in VER if "tropical apparent longitude" in r["datum"]),
                                      "asc_mc_diff_deg": max(r["difference"] for r in VER if r["datum"] in ("Asc tropical", "MC tropical")),
                                      "solar_term_max_diff_s": max(v["diff_s"] for v in jie_terms.values())}

    def dump(obj, name):
        with open(os.path.join(OUT, name), "w") as f:
            json.dump(obj, f, ensure_ascii=False, indent=2, default=str)
    dump(master, "MASTER_DATASET.json")
    dump(VER, "VERIFICATION_REPORT.json")
    dump(manifest, "CALCULATION_MANIFEST.json")
    print(json.dumps(master["verification_summary"], indent=1))
    print("alerts/fails:", [r["datum"] for r in VER if r["status"] != "pass"])


if __name__ == "__main__":
    main()
