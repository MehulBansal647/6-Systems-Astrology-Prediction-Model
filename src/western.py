"""Western / Hellenistic primary track: tropical, whole-sign houses, seven traditional planets."""
from __future__ import annotations

from astro_core import SIGNS, angdiff, norm, sign_of

SEVEN = ["Sun", "Moon", "Mercury", "Venus", "Mars", "Jupiter", "Saturn"]
DOMICILE = ["Mars", "Venus", "Mercury", "Moon", "Sun", "Mercury", "Venus", "Mars", "Jupiter",
            "Saturn", "Saturn", "Jupiter"]
EXALT = {"Sun": 0, "Moon": 1, "Mercury": 5, "Venus": 11, "Mars": 9, "Jupiter": 3, "Saturn": 6}
# Dorothean triplicity rulers: (day, night, participating)
TRIPLICITY = {"fire": ("Sun", "Jupiter", "Saturn"), "earth": ("Venus", "Moon", "Mars"),
              "air": ("Saturn", "Mercury", "Jupiter"), "water": ("Venus", "Mars", "Moon")}
ELEMENT = ["fire", "earth", "air", "water"] * 3
# Egyptian bounds: list of (planet, end_degree)
BOUNDS = [
    [("Jupiter", 6), ("Venus", 12), ("Mercury", 20), ("Mars", 25), ("Saturn", 30)],
    [("Venus", 8), ("Mercury", 14), ("Jupiter", 22), ("Saturn", 27), ("Mars", 30)],
    [("Mercury", 6), ("Jupiter", 12), ("Venus", 17), ("Mars", 24), ("Saturn", 30)],
    [("Mars", 7), ("Venus", 13), ("Mercury", 19), ("Jupiter", 26), ("Saturn", 30)],
    [("Jupiter", 6), ("Venus", 11), ("Saturn", 18), ("Mercury", 24), ("Mars", 30)],
    [("Mercury", 7), ("Venus", 17), ("Jupiter", 21), ("Mars", 28), ("Saturn", 30)],
    [("Saturn", 6), ("Mercury", 14), ("Jupiter", 21), ("Venus", 28), ("Mars", 30)],
    [("Mars", 7), ("Venus", 11), ("Mercury", 19), ("Jupiter", 24), ("Saturn", 30)],
    [("Jupiter", 12), ("Venus", 17), ("Mercury", 21), ("Saturn", 26), ("Mars", 30)],
    [("Mercury", 7), ("Jupiter", 14), ("Venus", 22), ("Saturn", 26), ("Mars", 30)],
    [("Mercury", 7), ("Venus", 13), ("Jupiter", 20), ("Mars", 25), ("Saturn", 30)],
    [("Venus", 12), ("Jupiter", 16), ("Mercury", 19), ("Mars", 28), ("Saturn", 30)],
]
CHALDEAN = ["Mars", "Sun", "Venus", "Mercury", "Moon", "Saturn", "Jupiter"]
MOIETY = {"Sun": 7.5, "Moon": 6.0, "Mercury": 3.5, "Venus": 3.5, "Mars": 3.75, "Jupiter": 4.5, "Saturn": 4.5}
ASPECTS = {0: "conjunction", 60: "sextile", 90: "square", 120: "trine", 180: "opposition"}
SIGN_DIST_FOR = {0: [0], 60: [2, 10], 90: [3, 9], 120: [4, 8], 180: [6]}
LILLY_POINTS = {"domicile": 5, "exaltation": 4, "triplicity": 3, "bound": 2, "face": 1,
                "detriment": -5, "fall": -4}
GOOD_PLACES = {1, 2, 4, 5, 7, 9, 10, 11}
BAD_PLACES = {6, 8, 12}


def bound_ruler(lon):
    s = int(norm(lon) // 30)
    d = norm(lon) - 30 * s
    for p, end in BOUNDS[s]:
        if d < end:
            return p
    return BOUNDS[s][-1][0]


def face_ruler(lon):
    i = int(norm(lon) // 10)
    return CHALDEAN[i % 7]


def essential(planet, lon, is_day):
    s = int(norm(lon) // 30)
    tri = TRIPLICITY[ELEMENT[s]]
    d = {
        "domicile": DOMICILE[s] == planet,
        "exaltation": EXALT.get(planet) == s,
        "triplicity": planet == (tri[0] if is_day else tri[1]) or planet == tri[2],
        "bound": bound_ruler(lon) == planet,
        "face": face_ruler(lon) == planet,
        "detriment": DOMICILE[(s + 6) % 12] == planet,
        "fall": EXALT.get(planet) is not None and (EXALT[planet] + 6) % 12 == s,
    }
    score = sum(LILLY_POINTS[k] for k, v in d.items() if v)
    major = ("domicile" if d["domicile"] else "exaltation" if d["exaltation"] else
             "detriment" if d["detriment"] else "fall" if d["fall"] else
             "minor_dignity_only" if (d["triplicity"] or d["bound"] or d["face"]) else "peregrine")
    return {"flags": d, "lilly_essential_score": score, "summary": major,
            "sign_ruler": DOMICILE[s], "exaltation_ruler": next((k for k, v in EXALT.items() if v == s), None),
            "triplicity_rulers": {"day": tri[0], "night": tri[1], "participating": tri[2]},
            "bound_ruler": bound_ruler(lon), "face_ruler": face_ruler(lon)}


def compute(pos_trop: dict, asc: float, mc: float, is_day: bool, sun_alt_deg: float) -> dict:
    asc_sign = int(norm(asc) // 30)
    lon = {p: pos_trop[p]["longitude"] for p in SEVEN}
    spd = {p: pos_trop[p]["speed_deg_per_day"] for p in SEVEN}

    def house_of(l):
        return (int(norm(l) // 30) - asc_sign) % 12 + 1

    houses = {h: {"sign": SIGNS[(asc_sign + h - 1) % 12], "ruler": DOMICILE[(asc_sign + h - 1) % 12],
                  "occupants": []} for h in range(1, 13)}
    sun = lon["Sun"]
    # Mercury sect: oriental (rises before Sun; longitude behind Sun) -> diurnal
    merc_oriental = norm(sun - lon["Mercury"]) < 180
    sect_member = {"Sun": "diurnal", "Jupiter": "diurnal", "Saturn": "diurnal",
                   "Moon": "nocturnal", "Venus": "nocturnal", "Mars": "nocturnal",
                   "Mercury": "diurnal" if merc_oriental else "nocturnal"}
    chart_sect = "diurnal" if is_day else "nocturnal"
    planets = {}
    for p in SEVEN:
        h = house_of(lon[p])
        houses[h]["occupants"].append(p)
        d = angdiff(lon[p], sun)
        if p == "Sun":
            vis = "n/a"
        elif d <= 17 / 60:
            vis = "cazimi"
        elif d <= 8.5:
            vis = "combust"
        elif d <= 15:
            vis = "under_the_beams"
        else:
            vis = "free_of_beams"
        planets[p] = {"longitude": lon[p], **sign_of(lon[p]), "house": h, "speed_deg_per_day": spd[p],
                      "retrograde": spd[p] < 0,
                      "angularity": "angular" if h in (1, 4, 7, 10) else "succedent" if h in (2, 5, 8, 11) else "cadent",
                      "place_quality": "good" if h in GOOD_PLACES else "bad" if h in BAD_PLACES else "middling",
                      "solar_phase": {"distance_from_sun_deg": d, "status": vis},
                      "sect_member": sect_member[p], "in_sect": sect_member[p] == chart_sect,
                      "essential_dignity": essential(p, lon[p], is_day)}
    benefic_of_sect = "Jupiter" if is_day else "Venus"
    malefic_of_sect = "Saturn" if is_day else "Mars"
    contrary_malefic = "Mars" if is_day else "Saturn"

    # dispositor chains (domicile)
    disp = {p: DOMICILE[planets[p]["sign_index"]] for p in SEVEN}
    chains = {}
    final = None
    for p in SEVEN:
        seen = [p]
        cur = p
        while True:
            nxt = disp[cur]
            if nxt in seen:
                break
            seen.append(nxt)
            cur = nxt
        chains[p] = seen
    finals = {p for p in SEVEN if disp[p] == p}
    final = sorted(finals)[0] if len(finals) == 1 else None

    # aspects with moiety orbs, sign-based
    asp = []
    for i, a in enumerate(SEVEN):
        for b in SEVEN[i + 1:]:
            sep = angdiff(lon[a], lon[b])
            sd = (planets[b]["sign_index"] - planets[a]["sign_index"]) % 12
            for ang, nm in ASPECTS.items():
                orb_allowed = MOIETY[a] + MOIETY[b]
                orb = abs(sep - ang)
                if sd in SIGN_DIST_FOR[ang] and orb <= orb_allowed:
                    # applying if |sep-ang| is decreasing
                    dt = 1 / 1440
                    la2 = lon[a] + spd[a] * dt
                    lb2 = lon[b] + spd[b] * dt
                    orb2 = abs(angdiff(la2, lb2) - ang)
                    asp.append({"a": a, "b": b, "aspect": nm, "exact_angle": ang, "separation_deg": sep,
                                "orb_deg": orb, "orb_allowed_deg": orb_allowed,
                                "state": "applying" if orb2 < orb else "separating"})
    # lots
    moon = lon["Moon"]
    if is_day:
        fortune = norm(asc + moon - sun)
        spirit = norm(asc + sun - moon)
    else:
        fortune = norm(asc + sun - moon)
        spirit = norm(asc + moon - sun)
    lots = {"Fortune": {"longitude": fortune, **sign_of(fortune), "house": house_of(fortune),
                        "formula": "day: Asc + Moon - Sun" if is_day else "night: Asc + Sun - Moon"},
            "Spirit": {"longitude": spirit, **sign_of(spirit), "house": house_of(spirit),
                       "formula": "day: Asc + Sun - Moon" if is_day else "night: Asc + Moon - Sun"}}
    return {"ascendant": {"longitude": asc, **sign_of(asc),
                          "sign_boundary_distance_deg": min(norm(asc) % 30, 30 - norm(asc) % 30)},
            "midheaven": {"longitude": mc, **sign_of(mc), "whole_sign_house": house_of(mc)},
            "sect": {"chart": chart_sect, "sun_true_altitude_deg": sun_alt_deg,
                     "benefic_of_sect": benefic_of_sect, "malefic_of_sect": malefic_of_sect,
                     "contrary_benefic": "Venus" if is_day else "Jupiter", "contrary_malefic": contrary_malefic,
                     "mercury_oriental": merc_oriental},
            "planets": planets, "houses": {str(k): v for k, v in houses.items()},
            "dispositors": disp, "dispositor_chains": chains, "final_dispositor": final,
            "mutual_receptions_domicile": sorted({tuple(sorted((a, b))) for a in SEVEN for b in SEVEN
                                                  if a != b and disp[a] == b and disp[b] == a}),
            "aspects": asp, "lots": lots,
            "conventions": {"bounds": "Egyptian", "triplicity": "Dorothean", "faces": "Chaldean decans",
                            "orbs": "Lilly moieties (sum), sign-based Ptolemaic aspects",
                            "essential_score": "Lilly points, informational only",
                            "solar_phase": "cazimi <=17', combust <=8.5 deg, under beams <=15 deg"}}


def profection(asc_sign_index: int, age_completed: int) -> dict:
    h = age_completed % 12 + 1
    si = (asc_sign_index + h - 1) % 12
    return {"age_completed": age_completed, "profected_house": h, "profected_sign": SIGNS[si],
            "lord_of_year": DOMICILE[si]}
