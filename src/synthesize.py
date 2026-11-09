"""Synthesis: project facts via the predeclared mapping registry; grade domains; temperament; chronology.

Reads output/MASTER_DATASET.json and config/mapping_registry.json. Writes output/SYNTHESIS.json.
No new facts are created here; every projection cites its datum and rule id.
"""
from __future__ import annotations

import json
import os
from datetime import date, datetime, timedelta

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "output")
M = json.load(open(os.path.join(OUT, "MASTER_DATASET.json")))
R = json.load(open(os.path.join(ROOT, "config", "mapping_registry.json")))
DOMS = list(R["domains"].keys())
REF = date.fromisoformat(json.load(open(os.path.join(OUT, "CALCULATION_MANIFEST.json")))["reference_date_for_timing"])

removed = {"missing_basis": [], "low_confidence": [], "duplication": [], "safety_scope": []}


def pol(score):
    return "supportive" if score >= 1.0 else "challenging" if score <= -1.0 else "mixed"


def prom(points):
    return "high" if points >= 2 else "medium" if points >= 1 else "low"


# ---------------- Jyotisha ----------------
def jyotisha_projections():
    j = M["jyotisha"]
    reg = R["jyotisha"]
    it = reg["polarity_items"]
    aspects_on = {}
    for a in j["graha_drishti"]:
        aspects_on.setdefault(a["target_house"], []).append(a["from"])
    per_dom = {}
    for h in range(1, 13):
        doms = reg["house_domain"][str(h)]
        H = j["houses"][str(h)]
        if not doms:
            if H["occupants"]:
                removed["safety_scope"].append(f"jyotisha house {h} occupants {H['occupants']} not projected (registry: unmapped house)")
            continue
        lord = H["lord"]
        g = j["grahas"][lord]
        items = [(f"lord {lord} dignity {g['dignity']}", it["lord_dignity"].get(g["dignity"], 0.0))]
        if g["house"] in (1, 4, 7, 10, 5, 9):
            items.append((f"lord {lord} in house {g['house']} (kendra/trikona)", it["lord_in_kendra_or_trikona"]))
        if g["house"] in (6, 8, 12):
            items.append((f"lord {lord} in house {g['house']} (dusthana)", it["lord_in_dusthana_6_8_12"]))
        if g.get("combustion", {}).get("combust"):
            items.append((f"lord {lord} combust", it["lord_combust"]))
        for o in H["occupants"]:
            nat = j["grahas"][o]["natural_nature"]
            items.append((f"occupant {o} (natural {nat})", it["occupant_natural_benefic"] if nat == "benefic" else it["occupant_natural_malefic"]))
        asp = aspects_on.get(h, [])
        for a in asp:
            if a == "Jupiter":
                items.append(("Jupiter drishti", it["jupiter_drishti_on_house"]))
            elif a in ("Saturn", "Mars"):
                items.append((f"{a} drishti", it["saturn_or_mars_drishti_on_house"]))
        score = sum(v for _, v in items)
        points = len(H["occupants"]) + 0.5 * len(asp)
        for d in doms:
            per_dom.setdefault(d, []).append({"house": h, "sign": H["sign"], "score": score, "points": points,
                                              "items": items, "occupants": H["occupants"], "aspected_by": asp})
    out = {}
    for d, lst in per_dom.items():
        score = sum(x["score"] for x in lst)
        points = max(x["points"] for x in lst)
        out[d] = {"domain": d, "system": "jyotisha", "cluster": "jyotisha", "prominence": prom(points),
                  "polarity": pol(score), "score": score, "confidence": "high",
                  "basis": lst, "mapping_rule": R["jyotisha"]["rule_id"]}
    return out


# ---------------- Western ----------------
def western_projections():
    w = M["western"]
    reg = R["western"]
    it = reg["polarity_items"]
    sect = w["sect"]
    lots_in = {}
    for nm, l in w["lots"].items():
        lots_in.setdefault(l["house"], []).append(nm)
    per_dom = {}
    for h in range(1, 13):
        doms = reg["house_domain"][str(h)]
        H = w["houses"][str(h)]
        if not doms:
            if H["occupants"]:
                removed["safety_scope"].append(f"western house {h} occupants {H['occupants']} not projected (registry: unmapped house)")
            continue
        ru = H["ruler"]
        p = w["planets"][ru]
        ed = p["essential_dignity"]["summary"]
        items = []
        if ed in ("domicile", "exaltation"):
            items.append((f"ruler {ru} in {ed}", it["ruler_domicile_or_exaltation"]))
        if ed in ("detriment", "fall"):
            items.append((f"ruler {ru} in {ed}", it["ruler_detriment_or_fall"]))
        if p["place_quality"] == "good":
            items.append((f"ruler {ru} in good place (house {p['house']})", it["ruler_in_good_place"]))
        elif p["place_quality"] == "bad":
            items.append((f"ruler {ru} in bad place (house {p['house']})", it["ruler_in_bad_place_6_8_12"]))
        ph = p["solar_phase"]["status"]
        if ph in ("combust", "under_the_beams"):
            items.append((f"ruler {ru} {ph}", it["ruler_combust_or_under_beams"]))
        elif ph == "cazimi":
            items.append((f"ruler {ru} cazimi", it["ruler_cazimi"]))
        for o in H["occupants"]:
            if o == sect["benefic_of_sect"]:
                items.append((f"occupant {o} benefic of sect", it["occupant_benefic_of_sect"]))
            elif o == sect["contrary_benefic"]:
                items.append((f"occupant {o} contrary benefic", it["occupant_contrary_benefic"]))
            elif o == sect["malefic_of_sect"]:
                items.append((f"occupant {o} malefic of sect", it["occupant_malefic_of_sect"]))
            elif o == sect["contrary_malefic"]:
                items.append((f"occupant {o} contrary malefic", it["occupant_contrary_malefic"]))
            else:
                items.append((f"occupant {o} (neutral in this rule)", 0.0))
        score = sum(v for _, v in items)
        points = len(H["occupants"]) + 0.5 * len(lots_in.get(h, []))
        for d in doms:
            per_dom.setdefault(d, []).append({"house": h, "sign": H["sign"], "score": score, "points": points,
                                              "items": items, "occupants": H["occupants"], "lots": lots_in.get(h, [])})
    out = {}
    for d, lst in per_dom.items():
        score = sum(x["score"] for x in lst)
        points = max(x["points"] for x in lst)
        out[d] = {"domain": d, "system": "western", "cluster": "western", "prominence": prom(points),
                  "polarity": pol(score), "score": score, "confidence": "high", "basis": lst,
                  "mapping_rule": R["western"]["rule_id"]}
    return out


# ---------------- Zi Wei ----------------
def ziwei_layout(palaces):
    reg = R["ziwei"]
    it = reg["polarity_items"]
    per_dom = {}
    for p in palaces:
        doms = reg["palace_domain"].get(p["name"], [])
        if not doms:
            continue
        if not p["majorStars"]:
            for d in doms:
                per_dom.setdefault(d, []).append({"palace": p["name"], "branch": p["earthlyBranch"], "empty": True})
            continue
        items = []
        for s in p["majorStars"]:
            items.append((f"{s['name']} brightness {s['brightness'] or 'n/a'}", it["brightness"].get(s["brightness"], 0.0)))
            if s["mutagen"]:
                items.append((f"{s['name']} 化{s['mutagen']}", it["birth_mutagen_on_major_star"][s["mutagen"]]))
        score = sum(v for _, v in items)
        points = len(p["majorStars"]) + sum(1 for s in p["majorStars"] if s["mutagen"])
        for d in doms:
            per_dom.setdefault(d, []).append({"palace": p["name"], "branch": p["earthlyBranch"], "empty": False,
                                              "score": score, "points": points, "items": items})
    out = {}
    for d, lst in per_dom.items():
        nonempty = [x for x in lst if not x["empty"]]
        if not nonempty:
            out[d] = {"silent": True, "basis": lst}
            continue
        score = sum(x["score"] for x in nonempty)
        points = max(x["points"] for x in nonempty)
        out[d] = {"silent": False, "prominence": prom(points), "polarity": pol(score), "score": score, "basis": lst}
    return out


def ziwei_projections():
    prim = ziwei_layout(M["ziwei"]["chart"]["palaces"])
    alt = ziwei_layout(M["ziwei"]["alt_leap_month_school_chart"]["palaces"])
    out = {}
    for d in DOMS:
        p, a = prim.get(d), alt.get(d)
        if not p or p.get("silent"):
            if p:
                removed["missing_basis"].append(f"ziwei {d}: mapped palace(s) empty -> silence, no projection")
            continue
        same = a is not None and not a.get("silent") and a["prominence"] == p["prominence"] and a["polarity"] == p["polarity"]
        out[d] = {"domain": d, "system": "ziwei", "cluster": "sinic", "prominence": p["prominence"], "polarity": p["polarity"],
                  "score": p["score"], "confidence": "medium" if same else "low", "basis": p["basis"],
                  "alt_leap_school": a, "mapping_rule": R["ziwei"]["rule_id"]}
    return out


# ---------------- BaZi ----------------
def bazi_projections():
    b = M["bazi"]
    reg = R["bazi"]
    male = M["input"]["normalized"]["gender"] == "male"
    W = reg["weights"]
    ug = b["useful_god"]
    A = ug["schools"]["UG-A strength-balance (扶抑, declared simplified)"]
    B = ug["schools"]["UG-B climate adjustment (调候, declared generic seasonal rule; not the full 穷通宝鉴 text)"]
    roles = ug["element_roles"]
    god_elem = {"比肩": roles["companion"], "劫财": roles["companion"], "食神": roles["output"], "伤官": roles["output"],
                "偏财": roles["wealth"], "正财": roles["wealth"], "七杀": roles["officer"], "正官": roles["officer"],
                "偏印": roles["resource"], "正印": roles["resource"]}
    acc = {}
    for pos, t in b["ten_gods"].items():
        if pos.endswith("_stem"):
            w = W["visible_stem"]
        else:
            k = int(pos.rsplit("_", 1)[1])
            w = [W["hidden_main"], W["hidden_middle"], W["hidden_residual"]][k]
        doms = list(reg["ten_god_domain"][t["ten_god"]])
        if male:
            doms += reg["ten_god_domain_male_extra"].get(t["ten_god"], [])
        for d in doms:
            acc.setdefault(d, []).append({"position": pos, "stem": t["stem"], "ten_god": t["ten_god"], "en": t["en"], "weight": w,
                                          "element": god_elem[t["ten_god"]]})
    out = {}
    for d, lst in acc.items():
        wsum = sum(x["weight"] for x in lst)
        elems = sorted({x["element"] for x in lst})
        pols, confs = [], []
        for e in elems:
            a_v = "supportive" if e in A["favorable"] else "challenging" if e in A["unfavorable"] else "mixed"
            b_v = "supportive" if e in B["favorable"] else "challenging" if e in B["unfavorable"] else None
            if b_v is None:
                pols.append(a_v)
                confs.append("low")
            elif b_v == a_v:
                pols.append(a_v)
                confs.append("medium")
            else:
                pols.append("mixed")
                confs.append("low")
        polarity = pols[0] if len(set(pols)) == 1 else "mixed"
        conf = "medium" if all(c == "medium" for c in confs) else "low"
        out[d] = {"domain": d, "system": "bazi", "cluster": "sinic", "prominence": prom(wsum) if wsum > 0 else "low",
                  "polarity": polarity, "weight_sum": wsum, "confidence": conf, "basis": lst,
                  "element_basis": dict(zip(elems, pols)), "mapping_rule": reg["rule_id"]}
    return out


def combine_sinic(zw, bzp):
    out = {}
    for d in DOMS:
        comps = [x for x in (zw.get(d), bzp.get(d)) if x]
        good = [x for x in comps if x["confidence"] in ("medium", "high")]
        for x in comps:
            if x not in good:
                removed["low_confidence"].append(f"{x['system']} {d} ({x['polarity']}, {x['prominence']}) excluded from Sinic vote: confidence {x['confidence']}")
        if not good:
            if comps:
                out[d] = {"domain": d, "cluster": "sinic", "prominence": max((c["prominence"] for c in comps), key=["low", "medium", "high"].index),
                          "polarity": "mixed", "confidence": "low", "components": comps, "note": "only low-confidence components"}
            continue
        pset = {x["polarity"] for x in good}
        polarity = good[0]["polarity"] if len(pset) == 1 else "mixed"
        if len(good) == 2 and len(pset) == 1:
            removed["duplication"].append(f"sinic {d}: BaZi and Zi Wei agree -> counted once (internal corroboration)")
        out[d] = {"domain": d, "cluster": "sinic", "prominence": max((c["prominence"] for c in good), key=["low", "medium", "high"].index),
                  "polarity": polarity, "confidence": "medium",
                  "internal_corroboration": len(good) == 2 and len(pset) == 1,
                  "internal_disagreement": len(pset) > 1, "components": comps}
    return out


def grade(projs):
    speaking = {c: p for c, p in projs.items()
                if p and p["confidence"] in ("medium", "high") and (p["prominence"] in ("medium", "high") or p["polarity"] != "mixed")}
    pols = [p["polarity"] for p in speaking.values()]
    if not speaking:
        g = "INSUFFICIENT"
    elif "supportive" in pols and "challenging" in pols:
        g = "DIVERGENT"
    else:
        k = max(pols.count(x) for x in set(pols))
        g = "STRONG" if k == 3 else "MODERATE" if k == 2 else "WEAK"
    shared = None
    if g in ("STRONG", "MODERATE"):
        shared = max(set(pols), key=pols.count)
    return g, sorted(speaking), shared


def temperament():
    j, w = M["jyotisha"], M["western"]
    zp = {p["earthlyBranch"]: p for p in M["ziwei"]["chart"]["palaces"]}
    za = {p["earthlyBranch"]: p for p in M["ziwei"]["alt_leap_month_school_chart"]["palaces"]}
    ming_p = M["ziwei"]["chart"]["soulBranch"]
    ming_a = M["ziwei"]["alt_leap_month_school_chart"]["soulBranch"]
    stars_p = {s["name"] for s in zp[ming_p]["majorStars"]}
    stars_a = {s["name"] for s in za[ming_a]["majorStars"]}
    vis = [t["ten_god"] for k, t in M["bazi"]["ten_gods"].items() if k.endswith("_stem")]
    good = ("exalted", "own", "moolatrikona")

    def jy(p):
        g = j["grahas"][p]
        return g["house"] in (1, 4, 7, 10) or g["dignity"] in good, f"{p}: house {g['house']}, {g['dignity']}"

    def we(p):
        q = w["planets"][p]
        return q["angularity"] == "angular" or q["essential_dignity"]["summary"] in ("domicile", "exaltation"), \
            f"{p}: house {q['house']} ({q['angularity']}), {q['essential_dignity']['summary']}"

    def zw(names, gods):
        both = bool(stars_p & names) and bool(stars_a & names)
        g = [x for x in vis if x in gods]
        return both or bool(g), f"Ming stars primary {sorted(stars_p)}, alt-school {sorted(stars_a)}; visible stem gods {vis}"

    axes = {}
    merc = j["grahas"]["Mercury"]
    wm = w["planets"]["Mercury"]
    dual = {2, 5, 8, 11}
    defs = {
        "T1": (jy("Sun"), we("Sun"), zw({"紫微", "太阳", "天府"}, {"正官", "七杀"})),
        "T2": (jy("Mars"), we("Mars"), zw({"七杀", "破军", "贪狼"}, {"七杀", "劫财"})),
        "T3": (jy("Moon"), we("Moon"), zw({"天同", "太阴", "天梁"}, {"正印", "偏印"})),
        "T4": ((merc["dignity"] in good and not merc["combustion"]["combust"], f"Mercury {merc['dignity']}, combust={merc['combustion']['combust']}"),
               (wm["essential_dignity"]["summary"] in ("domicile", "exaltation") and wm["solar_phase"]["status"] == "free_of_beams",
                f"Mercury {wm['essential_dignity']['summary']}, {wm['solar_phase']['status']}"),
               zw({"天机"}, {"食神", "伤官"})),
        "T5": ((j["lagna"]["sign_index"] in dual, f"Lagna {j['lagna']['sign']}"),
               (w["ascendant"]["sign_index"] in dual, f"Asc {w['ascendant']['sign']}"),
               ((bool(stars_p & {"天机", "贪狼"}) and bool(stars_a & {"天机", "贪狼"})) or (ming_p in "寅申巳亥" and ming_a in "寅申巳亥"),
                f"Ming primary {ming_p} {sorted(stars_p)}, alt {ming_a} {sorted(stars_a)}")),
        "T6": (jy("Saturn"), we("Saturn"), zw({"天府", "武曲", "天梁"}, {"正官"})),
    }
    names = {"T1": "Leadership/visibility", "T2": "Drive/initiative", "T3": "Nurturing/service", "T4": "Intellect/craft",
             "T5": "Adaptability", "T6": "Discipline/structure"}
    for k, (a, b, c) in defs.items():
        hits = [n for n, x in zip(("jyotisha", "western", "sinic"), (a, b, c)) if x[0]]
        axes[k] = {"axis": names[k], "rule": R["temperament"][k], "jyotisha": {"indicated": a[0], "basis": a[1]},
                   "western": {"indicated": b[0], "basis": b[1]}, "sinic": {"indicated": c[0], "basis": c[1]},
                   "clusters_indicating": hits, "count": len(hits)}
    return axes


# ---------------- Chronology ----------------
def chronology(horizon_years=10):
    j, w, b, z = M["jyotisha"], M["western"], M["bazi"], M["ziwei"]
    jreg = R["jyotisha"]["house_domain"]
    wreg = R["western"]["house_domain"]
    end = REF.replace(year=REF.year + horizon_years)
    bounds = {REF, end}
    ads = []
    for md in j["vimshottari"]["mahadashas"]:
        for ad in md["antardashas"]:
            s, e = datetime.fromisoformat(ad["start"]).date(), datetime.fromisoformat(ad["end"]).date()
            if e > REF and s < end:
                ads.append((s, e, md["lord"], ad["lord"]))
                bounds.update({max(s, REF), min(e, end)})
    for yy in range(REF.year - 1, end.year + 1):
        bounds.add(date(yy, 5, 29))
    annual = [(datetime.fromisoformat(a["start_lichun_utc"]).date(), datetime.fromisoformat(a["end_lichun_utc"]).date(), a)
              for a in b["annual_pillars"]]
    for s, e, _ in annual:
        bounds.update({s, e})
    zy = [(date.fromisoformat(y["start"]), date.fromisoformat(y["end_exclusive"]), y) for y in z["yearly_periods_observed"]]
    for s, e, _ in zy:
        bounds.update({s, e})
    bounds = sorted(x for x in bounds if REF <= x <= end)
    alt_by_branch = {p["earthlyBranch"]: p["name"] for p in z["alt_leap_month_school_chart"]["palaces"]}

    def jy_domains(lord):
        g = j["grahas"][lord]
        hs = set(g["houses_owned"]) | {g["house"]}
        return {d for h in hs for d in jreg[str(h)]}, sorted(hs)

    segs = []
    for s, e in zip(bounds[:-1], bounds[1:]):
        mid = s
        ad = next((x for x in ads if x[0] <= mid < x[1]), None)
        jd, jh = jy_domains(ad[3]) if ad else (set(), [])
        bd_ = mid.replace(year=mid.year) if True else mid
        age = mid.year - 2001 - (1 if (mid.month, mid.day) < (5, 29) else 0)
        ph = age % 12 + 1
        asc_i = w["ascendant"]["sign_index"]
        lord = ["Mars", "Venus", "Mercury", "Moon", "Sun", "Mercury", "Venus", "Mars", "Jupiter", "Saturn", "Saturn", "Jupiter"][(asc_i + ph - 1) % 12]
        lord_h = w["planets"][lord]["house"]
        wd = set(wreg[str(ph)]) | set(wreg[str(lord_h)])
        an = next((a for a in annual if a[0] <= mid < a[1]), None)
        sd = set()
        sinic_basis = {}
        if an:
            tg = an[2]["stem_ten_god"]
            sd |= set(R["bazi"]["ten_god_domain"][tg])
            if M["input"]["normalized"]["gender"] == "male":
                sd |= set(R["bazi"]["ten_god_domain_male_extra"].get(tg, []))
            sinic_basis["bazi_annual"] = {"pillar": an[2]["pillar"], "stem_ten_god": tg}
        zyp = next((y for y in zy if y[0] <= mid < y[1]), None)
        if zyp:
            br = zyp[2]["palace_branch"]
            pn, an_ = zyp[2]["natal_palace_at_branch"], alt_by_branch[br]
            zdp, zda = set(R["ziwei"]["palace_domain"].get(pn, [])), set(R["ziwei"]["palace_domain"].get(an_, []))
            sinic_basis["ziwei_yearly"] = {"branch": br, "palace_primary": pn, "palace_alt_leap_school": an_,
                                           "used": sorted(zdp & zda)}
            sd |= (zdp & zda)
        counts = {d: [c for c, ds in (("jyotisha", jd), ("western", wd), ("sinic", sd)) if d in ds] for d in DOMS}
        conv = {d: c for d, c in counts.items() if len(c) >= 2}
        segs.append({"start": s.isoformat(), "end": e.isoformat(),
                     "jyotisha": {"mahadasha": ad[2] if ad else None, "antardasha": ad[3] if ad else None,
                                  "houses": jh, "domains": sorted(jd)},
                     "western": {"age": age, "profected_house": ph, "lord_of_year": lord, "lord_natal_house": lord_h,
                                 "domains": sorted(wd)},
                     "sinic": {**sinic_basis, "domains": sorted(sd)},
                     "convergences": {d: {"clusters": c, "grade": "strong" if len(c) == 3 else "moderate"} for d, c in conv.items()}})
    # merge adjacent identical windows per domain
    windows = []
    for d in DOMS:
        cur = None
        for sg in segs:
            c = sg["convergences"].get(d)
            key = (tuple(c["clusters"]), c["grade"]) if c else None
            if key and cur and cur["key"] == key and cur["end"] == sg["start"]:
                cur["end"] = sg["end"]
            else:
                if cur:
                    windows.append(cur)
                cur = {"domain": d, "start": sg["start"], "end": sg["end"], "key": key, "clusters": list(key[0]), "grade": key[1]} if key else None
        if cur:
            windows.append(cur)
    for x in windows:
        x.pop("key")
    windows.sort(key=lambda x: (x["start"], x["domain"]))
    # base rate: chance that a domain is hit by >=2 clusters if activations were independent
    tot_days = sum((date.fromisoformat(s["end"]) - date.fromisoformat(s["start"])).days for s in segs)
    def frac(c):
        return sum(len(s[c]["domains"]) / 9 * (date.fromisoformat(s["end"]) - date.fromisoformat(s["start"])).days for s in segs) / tot_days
    pj, pw, ps = frac("jyotisha"), frac("western"), frac("sinic")
    p2 = pj * pw + pj * ps + pw * ps - 2 * pj * pw * ps
    p3 = pj * pw * ps
    return {"horizon": [REF.isoformat(), end.isoformat()], "segments": segs, "windows": windows,
            "base_rate": {"avg_fraction_domains_activated": {"jyotisha": pj, "western": pw, "sinic": ps},
                          "chance_domain_hit_by_>=2_clusters": p2, "chance_domain_hit_by_3_clusters": p3,
                          "expected_moderate_domains_per_segment_by_chance": 9 * p2},
            "context_backdrops": {
                "vimshottari_mahadasha": [ {k: md[k] for k in ("lord", "start", "end")} for md in j["vimshottari"]["mahadashas"]
                                          if datetime.fromisoformat(md["end"]).date() > REF and datetime.fromisoformat(md["start"]).date() < end],
                "bazi_da_yun": [p for p in b["da_yun"]["periods"] if datetime.fromisoformat(p["end"]).date() > REF and datetime.fromisoformat(p["start"]).date() < end],
                "ziwei_decadal": [x for x in z["decadal_periods_observed"] if date.fromisoformat(x["end_exclusive"]) > REF]}}


def main():
    jp, wp, zp, bp = jyotisha_projections(), western_projections(), ziwei_projections(), bazi_projections()
    sp = combine_sinic(zp, bp)
    domains = {}
    for d in DOMS:
        projs = {"jyotisha": jp.get(d), "western": wp.get(d), "sinic": sp.get(d)}
        g, speaking, shared = grade(projs)
        domains[d] = {"name": R["domains"][d], "grade": g, "speaking_clusters": speaking, "shared_polarity": shared,
                      "projections": {k: v for k, v in projs.items() if v},
                      "component_projections": {"ziwei": zp.get(d), "bazi": bp.get(d)}}
        for c in ("jyotisha", "western", "sinic"):
            if projs[c] is None:
                removed["missing_basis"].append(f"{c} {d}: no mapped datum (silence)")
    grades = {d: v["grade"] for d, v in domains.items()}
    div = sum(1 for g in grades.values() if g == "DIVERGENT")
    suff = sum(1 for g in grades.values() if g != "INSUFFICIENT")
    syn = {
        "registry_version": R["registry_version"], "reference_date": REF.isoformat(),
        "divergence": {"divergent_domains": div, "rate_over_all_9": div / 9, "domains_with_sufficient_evidence": suff,
                       "rate_over_sufficient": div / suff if suff else None},
        "grades": grades, "domains": domains, "temperament": temperament(), "chronology": chronology(),
        "overlays_non_voting": {
            "maya": {"calendar_round": M["maya"]["calendar_round"], "long_count": M["maya"]["long_count_str"],
                     "meaning": "omitted: no named Maya source available to attribute a day-sign meaning"},
            "tibetan": {"year": M["tibetan"]["year"], "meaning": "omitted: no sourced lineage text available"}},
        "removed_candidate_claims": {k: {"count": len(v), "items": v} for k, v in removed.items()},
    }
    with open(os.path.join(OUT, "SYNTHESIS.json"), "w") as f:
        json.dump(syn, f, ensure_ascii=False, indent=2, default=str)
    print(json.dumps({"grades": grades, "divergence": syn["divergence"]}, indent=1))
    for d, v in domains.items():
        print(d, v["grade"], {c: (p["prominence"], p["polarity"], p["confidence"]) for c, p in v["projections"].items()})
    for k, v in syn["temperament"].items():
        print(k, v["axis"], v["clusters_indicating"])
    print(json.dumps(syn["chronology"]["base_rate"], indent=1))
    for x in syn["chronology"]["windows"][:40]:
        print(x)
    print({k: v["count"] for k, v in syn["removed_candidate_claims"].items()})


if __name__ == "__main__":
    main()
