"""Shared astronomical base: Swiss Ephemeris (primary) and JPL DE421 via Skyfield (validator).

Facts only. No interpretation.
"""
from __future__ import annotations

import math
import os
from datetime import datetime, timedelta, timezone

import swisseph as swe
from skyfield.api import load, load_file, wgs84
from skyfield import almanac
from skyfield.framelib import ecliptic_frame
from skyfield.nutationlib import iau2000a_radians, mean_obliquity
import skyfield_data

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EPHE_PATH = os.path.join(ROOT, "ephe")
DE_PATH = os.path.join(os.path.dirname(skyfield_data.__file__), "data", "de421.bsp")

swe.set_ephe_path(EPHE_PATH)

PLANETS = {
    "Sun": swe.SUN, "Moon": swe.MOON, "Mercury": swe.MERCURY, "Venus": swe.VENUS,
    "Mars": swe.MARS, "Jupiter": swe.JUPITER, "Saturn": swe.SATURN,
    "Uranus": swe.URANUS, "Neptune": swe.NEPTUNE, "Pluto": swe.PLUTO,
}
SKY_NAMES = {
    "Sun": "sun", "Moon": "moon", "Mercury": "mercury", "Venus": "venus",
    "Mars": "mars", "Jupiter": "jupiter barycenter", "Saturn": "saturn barycenter",
    "Uranus": "uranus barycenter", "Neptune": "neptune barycenter", "Pluto": "pluto barycenter",
}
SIGNS = ["Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo", "Libra", "Scorpio",
         "Sagittarius", "Capricorn", "Aquarius", "Pisces"]

FLAGS = swe.FLG_SWIEPH | swe.FLG_SPEED

_ts = load.timescale(builtin=True)
_eph = load_file(DE_PATH)


def norm(x: float) -> float:
    return x % 360.0


def angdiff(a: float, b: float) -> float:
    """Smallest absolute angular difference in degrees."""
    d = abs(norm(a) - norm(b)) % 360.0
    return min(d, 360.0 - d)


def sign_of(lon: float) -> dict:
    lon = norm(lon)
    i = int(lon // 30)
    return {"sign_index": i, "sign": SIGNS[i], "degree_in_sign": lon - 30 * i}


def jd_from_utc(dt_utc: datetime) -> tuple[float, float]:
    """Return (jd_tt, jd_ut) using Swiss Ephemeris UTC conversion (leap seconds aware)."""
    sec = dt_utc.second + dt_utc.microsecond / 1e6
    jd_et, jd_ut = swe.utc_to_jd(dt_utc.year, dt_utc.month, dt_utc.day,
                                 dt_utc.hour, dt_utc.minute, sec, swe.GREG_CAL)
    return jd_et, jd_ut


def jd_ut_to_utc(jd_ut: float) -> datetime:
    y, m, d, h, mi, s = swe.jdut1_to_utc(jd_ut, swe.GREG_CAL)
    whole = int(s)
    micro = int(round((s - whole) * 1e6))
    if micro >= 1_000_000:
        whole += 1
        micro -= 1_000_000
    base = datetime(y, m, d, h, mi, 0, tzinfo=timezone.utc)
    return base + timedelta(seconds=whole, microseconds=micro)


def swe_planets(jd_ut: float, sidereal_mode: int | None = None) -> dict:
    flags = FLAGS
    if sidereal_mode is not None:
        swe.set_sid_mode(sidereal_mode, 0, 0)
        flags |= swe.FLG_SIDEREAL
    out = {}
    for name, pid in PLANETS.items():
        xx, _ = swe.calc_ut(jd_ut, pid, flags)
        out[name] = {"longitude": xx[0], "latitude": xx[1], "distance_au": xx[2],
                     "speed_deg_per_day": xx[3], "retrograde": xx[3] < 0}
    for nname, nid in (("MeanNode", swe.MEAN_NODE), ("TrueNode", swe.TRUE_NODE)):
        xx, _ = swe.calc_ut(jd_ut, nid, flags)
        out[nname] = {"longitude": xx[0], "latitude": xx[1], "speed_deg_per_day": xx[3],
                      "retrograde": xx[3] < 0}
    return out


def skyfield_planets(dt_utc: datetime) -> dict:
    t = _ts.from_datetime(dt_utc)
    earth = _eph["earth"]
    out = {}
    for name, key in SKY_NAMES.items():
        if name == "Pluto":
            # DE421 includes Pluto barycenter; keep for completeness.
            pass
        app = earth.at(t).observe(_eph[key]).apparent()
        lat, lon, dist = app.frame_latlon(ecliptic_frame)
        out[name] = {"longitude": lon.degrees % 360.0, "latitude": lat.degrees}
    return out


def swe_houses(jd_ut: float, lat: float, lon: float, hsys: bytes, sidereal_mode: int | None = None):
    if sidereal_mode is not None:
        swe.set_sid_mode(sidereal_mode, 0, 0)
        cusps, ascmc = swe.houses_ex(jd_ut, lat, lon, hsys, swe.FLG_SIDEREAL)
    else:
        cusps, ascmc = swe.houses_ex(jd_ut, lat, lon, hsys)
    return list(cusps), {"Asc": ascmc[0], "MC": ascmc[1], "ARMC": ascmc[2], "Vertex": ascmc[3]}


def independent_asc_mc(dt_utc: datetime, lat: float, lon: float) -> dict:
    """Ascendant/MC from Skyfield GAST + IAU2000A true obliquity and spherical trig.

    Code path shares nothing with Swiss Ephemeris.
    """
    t = _ts.from_datetime(dt_utc)
    ramc = math.radians((t.gast * 15.0 + lon) % 360.0)
    dpsi, deps = iau2000a_radians(t)
    eps = math.radians(mean_obliquity(t.tdb) / 3600.0) + deps
    phi = math.radians(lat)
    asc = math.degrees(math.atan2(math.cos(ramc),
                                  -(math.sin(ramc) * math.cos(eps) + math.tan(phi) * math.sin(eps))))
    mc = math.degrees(math.atan2(math.sin(ramc), math.cos(ramc) * math.cos(eps)))
    return {"Asc": asc % 360.0, "MC": mc % 360.0, "RAMC_deg": math.degrees(ramc),
            "true_obliquity_deg": math.degrees(eps)}


def sun_alt(dt_utc: datetime, lat: float, lon: float) -> float:
    t = _ts.from_datetime(dt_utc)
    obs = _eph["earth"] + wgs84.latlon(lat, lon)
    alt, az, _ = obs.at(t).observe(_eph["sun"]).apparent().altaz()
    return alt.degrees


def swe_sun_alt(jd_ut: float, lat: float, lon: float) -> float:
    xx, _ = swe.calc_ut(jd_ut, swe.SUN, swe.FLG_SWIEPH | swe.FLG_EQUATORIAL)
    hor = swe.azalt(jd_ut, swe.EQU2HOR, (lon, lat, 0.0), 0.0, 0.0, (xx[0], xx[1], xx[2]))
    return hor[1]  # true (unrefracted) altitude


def swe_rise_set(jd_ut_start: float, lat: float, lon: float) -> dict:
    geopos = (lon, lat, 0.0)
    out = {}
    for label, flag in (("sunrise", swe.CALC_RISE), ("sunset", swe.CALC_SET)):
        res, tret = swe.rise_trans(jd_ut_start, swe.SUN, flag, geopos, 1013.25, 15.0, swe.FLG_SWIEPH)
        out[label] = tret[0]
    return out


def skyfield_rise_set(dt0: datetime, dt1: datetime, lat: float, lon: float) -> list:
    t0, t1 = _ts.from_datetime(dt0), _ts.from_datetime(dt1)
    f = almanac.sunrise_sunset(_eph, wgs84.latlon(lat, lon))
    times, events = almanac.find_discrete(t0, t1, f)
    return [(t.utc_datetime(), "sunrise" if e else "sunset") for t, e in zip(times, events)]


def swe_solar_crossing(target_lon: float, jd_ut_start: float) -> float:
    return swe.solcross_ut(target_lon, jd_ut_start, swe.FLG_SWIEPH)


def skyfield_solar_crossing(target_lon: float, dt_lo: datetime, dt_hi: datetime) -> datetime:
    """Bisection on Skyfield apparent solar longitude (independent of swe)."""
    def f(dt):
        t = _ts.from_datetime(dt)
        app = _eph["earth"].at(t).observe(_eph["sun"]).apparent()
        _, lon, _ = app.frame_latlon(ecliptic_frame)
        d = (lon.degrees - target_lon + 540.0) % 360.0 - 180.0
        return d
    lo, hi = dt_lo, dt_hi
    flo = f(lo)
    for _ in range(60):
        mid = lo + (hi - lo) / 2
        fm = f(mid)
        if (fm < 0) == (flo < 0):
            lo, flo = mid, fm
        else:
            hi = mid
        if (hi - lo).total_seconds() < 0.05:
            break
    return lo + (hi - lo) / 2


def swe_moon_sun_sidereal(jd_ut: float, mode: int) -> tuple[float, float]:
    swe.set_sid_mode(mode, 0, 0)
    m, _ = swe.calc_ut(jd_ut, swe.MOON, swe.FLG_SWIEPH | swe.FLG_SIDEREAL)
    return m[0], swe.get_ayanamsa_ex_ut(jd_ut, swe.FLG_SWIEPH)[1]


def equation_of_time_minutes(jd_ut: float) -> float:
    e = swe.time_equ(jd_ut)
    e = e[1] if isinstance(e, tuple) else e
    return e * 1440.0
