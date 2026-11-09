"""Jyotisha (Parashari track): sidereal Lahiri, whole-sign houses, mean node primary."""
from __future__ import annotations

from datetime import datetime, timedelta, timezone

import swisseph as swe

from astro_core import SIGNS, angdiff, norm, sign_of

GRAHAS = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Rahu", "Ketu"]
SEVEN = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"]

SIGN_LORD = ["Mars", "Venus", "Mercury", "Moon", "Sun", "Mercury", "Venus", "Mars", "Jupiter",
             "Saturn", "Saturn", "Jupiter"]
EXALT = {"Sun": 0, "Moon": 1, "Mars": 9, "Mercury": 5, "Jupiter": 3, "Venus": 11, "Saturn": 6}
DEBIL = {k: (v + 6) % 12 for k, v in EXALT.items()}
# Moolatrikona (BPHS): sign index, start deg, end deg
MOOLA = {"Sun": (4, 0, 20), "Moon": (1, 3, 30), "Mars": (0, 0, 12), "Mercury": (5, 16, 20),
         "Jupiter": (8, 0, 10), "Venus": (6, 0, 15), "Saturn": (10, 0, 20)}
OWN = {"Sun": [4], "Moon": [3], "Mars": [0, 7], "Mercury": [2, 5], "Jupiter": [8, 11],
       "Venus": [1, 6], "Saturn": [9, 10]}
# Naisargika (natural) relationships, BPHS
NAT = {
    "Sun": {"friend": ["Moon", "Mars", "Jupiter"], "neutral": ["Mercury"], "enemy": ["Venus", "Saturn"]},
    "Moon": {"friend": ["Sun", "Mercury"], "neutral": ["Mars", "Jupiter", "Venus", "Saturn"], "enemy": []},
    "Mars": {"friend": ["Sun", "Moon", "Jupiter"], "neutral": ["Venus", "Saturn"], "enemy": ["Mercury"]},
    "Mercury": {"friend": ["Sun", "Venus"], "neutral": ["Mars", "Jupiter", "Saturn"], "enemy": ["Moon"]},
    "Jupiter": {"friend": ["Sun", "Moon", "Mars"], "neutral": ["Saturn"], "enemy": ["Mercury", "Venus"]},
    "Venus": {"friend": ["Mercury", "Saturn"], "neutral": ["Mars", "Jupiter"], "enemy": ["Sun", "Moon"]},
    "Saturn": {"friend": ["Mercury", "Venus"], "neutral": ["Jupiter"], "enemy": ["Sun", "Moon", "Mars"]},
}
# Combustion orbs (degrees of longitude from Sun); (direct, retrograde)
COMBUST = {"Moon": (12, 12), "Mars": (17, 17), "Mercury": (14, 12), "Jupiter": (11, 11),
           "Venus": (10, 8), "Saturn": (15, 15)}
SPECIAL_ASPECTS = {"Mars": [4, 7, 8], "Jupiter": [5, 7, 9], "Saturn": [3, 7, 10]}
NAKSHATRAS = ["Ashwini", "Bharani", "Krittika", "Rohini", "Mrigashira", "Ardra", "Punarvasu", "Pushya",
              "Ashlesha", "Magha", "Purva Phalguni", "Uttara Phalguni", "Hasta", "Chitra", "Swati",
              "Vishakha", "Anuradha", "Jyeshtha", "Mula", "Purva Ashadha", "Uttara Ashadha", "Shravana",
              "Dhanishta", "Shatabhisha", "Purva Bhadrapada", "Uttara Bhadrapada", "Revati"]
DASHA_ORDER = ["Ketu", "Venus", "Sun", "Moon", "Mars", "Rahu", "Jupiter", "Saturn", "Mercury"]
DASHA_YEARS = {"Ketu": 7, "Venus": 20, "Sun": 6, "Moon": 10, "Mars": 7, "Rahu": 18, "Jupiter": 16,
               "Saturn": 19, "Mercury": 17}
DASHA_YEAR_DAYS = 365.25
NAT_BENEFIC = {"Jupiter", "Venus", "Mercury"}  # Moon added when waxing
NAT_MALEFIC = {"Sun", "Mars", "Saturn", "Rahu", "Ketu"}

NAK_SPAN = 360.0 / 27.0


def nakshatra(lon: float) -> dict:
    lon = norm(lon)
    i = int(lon // NAK_SPAN)
    within = lon - i * NAK_SPAN
    pada = int(within // (NAK_SPAN / 4)) + 1
    return {"index": i, "name": NAKSHATRAS[i], "lord": DASHA_ORDER[i % 9], "pada": pada,
            "fraction_elapsed": within / NAK_SPAN,
            "distance_to_pada_boundary_deg": min(within % (NAK_SPAN / 4), NAK_SPAN / 4 - within % (NAK_SPAN / 4))}


def d9_sign(lon: float) -> int:
    return int(norm(lon) * 9 // 30) % 12


def d9_boundary_distance(lon: float) -> float:
    span = 30.0 / 9
    r = norm(lon) % span
    return min(r, span - r)


def d10_sign(lon: float) -> int:
    lon = norm(lon)
    s = int(lon // 30)
    part = int((lon - 30 * s) // 3)
    start = s if s % 2 == 0 else (s + 8) % 12  # odd signs (Aries=0 index) from same sign; even from 9th
    return (start + part) % 12


def d10_boundary_distance(lon: float) -> float:
    r = norm(lon) % 3.0
    return min(r, 3.0 - r)


def dignity(planet: str, lon: float) -> str:
    if planet not in SEVEN:
        return "not_assessed_node"
    s = int(norm(lon) // 30)
    deg = norm(lon) - 30 * s
    if EXALT[planet] == s:
        return "exalted"
    if DEBIL[planet] == s:
        return "debilitated"
    ms, a, b = MOOLA[planet]
    if ms == s and a <= deg < b:
        return "moolatrikona"
    if s in OWN[planet]:
        return "own"
    lord = SIGN_LORD[s]
    for rel in ("friend", "neutral", "enemy"):
        if lord in NAT[planet][rel]:
            return {"friend": "friend_sign", "neutral": "neutral_sign", "enemy": "enemy_sign"}[rel]
    return "unknown"


DIGNITY_SCORE = {"exalted": 1.0, "moolatrikona": 1.0, "own": 1.0, "friend_sign": 0.5,
                 "neutral_sign": 0.0, "enemy_sign": -0.5, "debilitated": -1.0}


def compute(pos_sid: dict, asc_sid: float, sun_trop: float, moon_trop: float, birth_utc: datetime,
            node_key: str = "MeanNode") -> dict:
    lagna_sign = int(norm(asc_sid) // 30)
    lon = {p: pos_sid[p]["longitude"] for p in SEVEN}
    lon["Rahu"] = pos_sid[node_key]["longitude"]
    lon["Ketu"] = norm(lon["Rahu"] + 180.0)
    speed = {p: pos_sid[p]["speed_deg_per_day"] for p in SEVEN}
    speed["Rahu"] = pos_sid[node_key]["speed_deg_per_day"]
    speed["Ketu"] = speed["Rahu"]

    elong = norm(moon_trop - sun_trop)
    moon_waxing = elong < 180.0
    benefics = set(NAT_BENEFIC) | ({"Moon"} if moon_waxing else set())
    malefics = set(NAT_MALEFIC) | (set() if moon_waxing else {"Moon"})

    def house_of(l):
        return (int(norm(l) // 30) - lagna_sign) % 12 + 1

    houses = {}
    for h in range(1, 13):
        si = (lagna_sign + h - 1) % 12
        houses[h] = {"sign": SIGNS[si], "sign_index": si, "lord": SIGN_LORD[si], "occupants": []}

    grahas = {}
    for p in GRAHAS:
        l = lon[p]
        h = house_of(l)
        houses[h]["occupants"].append(p)
        sg = sign_of(l)
        g = {
            "sidereal_longitude": l, **sg, "house": h, "speed_deg_per_day": speed[p],
            "retrograde": speed[p] < 0 if p not in ("Rahu", "Ketu") else True,
            "nakshatra": nakshatra(l), "dignity": dignity(p, l),
            "d9_sign": SIGNS[d9_sign(l)], "d9_boundary_distance_deg": d9_boundary_distance(l),
            "d10_sign": SIGNS[d10_sign(l)], "d10_boundary_distance_deg": d10_boundary_distance(l),
            "houses_owned": [hh for hh in range(1, 13) if houses[hh]["lord"] == p],
            "natural_nature": "benefic" if p in benefics else "malefic",
        }
        if p in COMBUST:
            orb = COMBUST[p][1 if speed[p] < 0 else 0]
            dist = angdiff(l, lon["Sun"])
            g["combustion"] = {"distance_from_sun_deg": dist, "orb_deg": orb, "combust": dist < orb,
                               "margin_deg": dist - orb}
        grahas[p] = g

    # planetary war (graha yuddha): Mars, Mercury, Jupiter, Venus, Saturn within 1 deg
    war = []
    tw = ["Mars", "Mercury", "Jupiter", "Venus", "Saturn"]
    for i, a in enumerate(tw):
        for b in tw[i + 1:]:
            d = angdiff(lon[a], lon[b])
            if d < 1.0:
                war.append({"planets": [a, b], "separation_deg": d})

    # graha drishti (whole-sign)
    aspects = []
    for p in GRAHAS:
        if p in ("Rahu", "Ketu"):
            continue  # node aspects excluded in this school configuration
        for n in SPECIAL_ASPECTS.get(p, [7]):
            target_house = (grahas[p]["house"] + n - 1 - 1) % 12 + 1
            aspects.append({"from": p, "aspect_nth": n, "target_house": target_house,
                            "target_sign": houses[target_house]["sign"],
                            "targets_occupied_by": [q for q in houses[target_house]["occupants"] if q != p]})

    # functional nature (declared rule set FN-1)
    func = {}
    for p in SEVEN:
        owned = grahas[p]["houses_owned"]
        if any(h in (5, 9) for h in owned):
            kend = [h for h in owned if h in (4, 7, 10)]
            func[p] = {"status": "yogakaraka" if kend else "functional_benefic", "rule": "FN-1a owns 5th/9th"}
        elif 1 in owned:
            func[p] = {"status": "functional_benefic", "rule": "FN-1b lagna lord"}
        elif any(h in (3, 6, 11) for h in owned):
            func[p] = {"status": "functional_malefic", "rule": "FN-1c owns 3rd/6th/11th"}
        elif 8 in owned:
            func[p] = {"status": "functional_malefic", "rule": "FN-1d owns 8th"}
        else:
            func[p] = {"status": "functional_neutral", "rule": "FN-1e kendra/other only"}
    for p in SEVEN:
        grahas[p]["functional_status"] = func[p]

    asc_info = {"sidereal_longitude": asc_sid, **sign_of(asc_sid), "nakshatra": nakshatra(asc_sid),
                "d9_sign": SIGNS[d9_sign(asc_sid)], "d9_boundary_distance_deg": d9_boundary_distance(asc_sid),
                "d10_sign": SIGNS[d10_sign(asc_sid)], "d10_boundary_distance_deg": d10_boundary_distance(asc_sid),
                "sign_boundary_distance_deg": min(norm(asc_sid) % 30, 30 - norm(asc_sid) % 30)}

    yogas = evaluate_yogas(grahas, houses, lagna_sign, lon)
    dashas = vimshottari(lon["Moon"], birth_utc)

    return {"lagna": asc_info, "grahas": grahas, "houses": {str(k): v for k, v in houses.items()},
            "graha_drishti": aspects, "planetary_war": war,
            "moon_elongation_deg": elong, "moon_waxing": moon_waxing,
            "d9": {"Lagna": asc_info["d9_sign"], **{p: grahas[p]["d9_sign"] for p in GRAHAS}},
            "d10": {"Lagna": asc_info["d10_sign"], **{p: grahas[p]["d10_sign"] for p in GRAHAS}},
            "yogas": yogas, "vimshottari": dashas}


def evaluate_yogas(grahas, houses, lagna_sign, lon):
    """Declared whitelist only. Each entry records rule and satisfying placements."""
    out = []
    moon_sign = grahas["Moon"]["sign_index"]

    def from_moon(p):
        return (grahas[p]["sign_index"] - moon_sign) % 12 + 1

    # Y1 Gajakesari: Jupiter in kendra (1/4/7/10) from Moon
    fm = from_moon("Jupiter")
    out.append({"id": "Y1", "name": "Gajakesari", "rule": "Jupiter in 1st/4th/7th/10th sign from Moon",
                "present": fm in (1, 4, 7, 10), "basis": {"jupiter_house_from_moon": fm}})
    # Y2 Budha-Aditya: Sun and Mercury in same sign
    out.append({"id": "Y2", "name": "Budha-Aditya", "rule": "Sun and Mercury in the same sign",
                "present": grahas["Sun"]["sign_index"] == grahas["Mercury"]["sign_index"],
                "basis": {"sun_sign": grahas["Sun"]["sign"], "mercury_sign": grahas["Mercury"]["sign"]}})
    # Y3 Pancha Mahapurusha
    names = {"Mars": "Ruchaka", "Mercury": "Bhadra", "Jupiter": "Hamsa", "Venus": "Malavya", "Saturn": "Shasha"}
    for p, nm in names.items():
        cond = grahas[p]["dignity"] in ("own", "exalted", "moolatrikona") and grahas[p]["house"] in (1, 4, 7, 10)
        out.append({"id": "Y3-" + p, "name": nm + " (Pancha Mahapurusha)",
                    "rule": f"{p} in own/exaltation/moolatrikona sign AND in kendra from Lagna",
                    "present": cond, "basis": {"dignity": grahas[p]["dignity"], "house": grahas[p]["house"]}})
    # Y4 Chandra-Mangala
    out.append({"id": "Y4", "name": "Chandra-Mangala", "rule": "Moon and Mars in the same sign",
                "present": grahas["Moon"]["sign_index"] == grahas["Mars"]["sign_index"],
                "basis": {"moon_sign": grahas["Moon"]["sign"], "mars_sign": grahas["Mars"]["sign"]}})
    # Y5 Kemadruma with one declared cancellation rule
    excl = {"Sun", "Rahu", "Ketu", "Moon"}
    second = [p for p in grahas if p not in excl and from_moon(p) == 2]
    twelfth = [p for p in grahas if p not in excl and from_moon(p) == 12]
    kem = not second and not twelfth
    kendra_moon = [p for p in grahas if p not in {"Moon", "Rahu", "Ketu"} and from_moon(p) in (1, 4, 7, 10)]
    out.append({"id": "Y5", "name": "Kemadruma",
                "rule": "No graha other than Sun/Rahu/Ketu in 2nd or 12th sign from Moon",
                "present": kem, "basis": {"in_2nd_from_moon": second, "in_12th_from_moon": twelfth},
                "cancellation_rule": "Y5c: any graha (excl. Moon and nodes) in kendra from Moon cancels",
                "cancelled": kem and bool(kendra_moon), "cancellation_basis": kendra_moon})
    # Y6 Raja yoga: kendra lord and trikona lord conjoined (same sign) or in sign exchange
    kendra_lords = {houses[h]["lord"] for h in (1, 4, 7, 10)}
    trikona_lords = {houses[h]["lord"] for h in (1, 5, 9)}
    found = []
    for a in sorted(kendra_lords):
        for b in sorted(trikona_lords):
            if a == b:
                continue
            if grahas[a]["sign_index"] == grahas[b]["sign_index"]:
                found.append({"type": "conjunction", "kendra_lord": a, "trikona_lord": b,
                              "sign": grahas[a]["sign"]})
            elif (SIGN_LORD[grahas[a]["sign_index"]] == b and SIGN_LORD[grahas[b]["sign_index"]] == a):
                found.append({"type": "exchange (parivartana)", "kendra_lord": a, "trikona_lord": b})
    out.append({"id": "Y6", "name": "Raja yoga (kendra-trikona lord conjunction/exchange)",
                "rule": "Lord of 1/4/7/10 and lord of 1/5/9 (different planets) in same sign or exchanging signs",
                "present": bool(found), "basis": found})
    return out


def vimshottari(moon_sid: float, birth_utc: datetime) -> dict:
    nk = nakshatra(moon_sid)
    lord = nk["lord"]
    start_idx = DASHA_ORDER.index(lord)
    elapsed_years = DASHA_YEARS[lord] * nk["fraction_elapsed"]
    day = timedelta(days=DASHA_YEAR_DAYS)
    cycle_start = birth_utc - day * elapsed_years
    mds = []
    t = cycle_start
    for k in range(9):
        md = DASHA_ORDER[(start_idx + k) % 9]
        dur = DASHA_YEARS[md]
        md_end = t + day * dur
        ads = []
        ta = t
        for j in range(9):
            ad = DASHA_ORDER[(DASHA_ORDER.index(md) + j) % 9]
            ad_dur = dur * DASHA_YEARS[ad] / 120.0
            ad_end = ta + day * ad_dur
            ads.append({"lord": ad, "start": ta.isoformat(), "end": ad_end.isoformat()})
            ta = ad_end
        mds.append({"lord": md, "start": t.isoformat(), "end": md_end.isoformat(), "years": dur,
                    "antardashas": ads})
        t = md_end
    return {"moon_nakshatra": nk["name"], "nakshatra_lord": lord,
            "balance_at_birth_years": DASHA_YEARS[lord] - elapsed_years,
            "year_length_days": DASHA_YEAR_DAYS, "cycle_start_theoretical": cycle_start.isoformat(),
            "total_years": sum(DASHA_YEARS.values()), "mahadashas": mds}


def pratyantar(md: str, ad: str, ad_start: datetime, ad_end: datetime) -> list:
    total = (ad_end - ad_start)
    out = []
    t = ad_start
    for j in range(9):
        pd = DASHA_ORDER[(DASHA_ORDER.index(ad) + j) % 9]
        e = t + total * (DASHA_YEARS[pd] / 120.0)
        out.append({"lord": pd, "start": t.isoformat(), "end": e.isoformat()})
        t = e
    return out
