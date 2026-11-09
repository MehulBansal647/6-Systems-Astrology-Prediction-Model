"""BaZi Four Pillars. Pillars cross-checked: lunar_python vs. independent arithmetic + exact solar terms."""
from __future__ import annotations

from datetime import datetime, timedelta, timezone

from lunar_python import Solar

STEMS = "甲乙丙丁戊己庚辛壬癸"
BRANCHES = "子丑寅卯辰巳午未申酉戌亥"
STEM_PINYIN = ["Jia", "Yi", "Bing", "Ding", "Wu", "Ji", "Geng", "Xin", "Ren", "Gui"]
BRANCH_PINYIN = ["Zi", "Chou", "Yin", "Mao", "Chen", "Si", "Wu", "Wei", "Shen", "You", "Xu", "Hai"]
STEM_ELEM = ["Wood", "Wood", "Fire", "Fire", "Earth", "Earth", "Metal", "Metal", "Water", "Water"]
BRANCH_ELEM = ["Water", "Earth", "Wood", "Wood", "Earth", "Fire", "Fire", "Earth", "Metal", "Metal", "Earth", "Water"]
HIDDEN = {"子": "癸", "丑": "己癸辛", "寅": "甲丙戊", "卯": "乙", "辰": "戊乙癸", "巳": "丙戊庚",
          "午": "丁己", "未": "己丁乙", "申": "庚壬戊", "酉": "辛", "戌": "戊辛丁", "亥": "壬甲"}
HIDDEN_WEIGHTS = [1.0, 0.5, 0.3]  # main, middle, residual qi (declared rule set DM-1)
GEN = {"Wood": "Fire", "Fire": "Earth", "Earth": "Metal", "Metal": "Water", "Water": "Wood"}
CTRL = {"Wood": "Earth", "Earth": "Water", "Water": "Fire", "Fire": "Metal", "Metal": "Wood"}
TEN_GOD_EN = {"比肩": "Friend (Companion)", "劫财": "Rob Wealth", "食神": "Eating God", "伤官": "Hurting Officer",
              "偏财": "Indirect Wealth", "正财": "Direct Wealth", "七杀": "Seven Killings", "正官": "Direct Officer",
              "偏印": "Indirect Resource", "正印": "Direct Resource"}
# Jie (sectional) terms: solar longitude -> month branch
JIE = [(315, "寅"), (345, "卯"), (15, "辰"), (45, "巳"), (75, "午"), (105, "未"), (135, "申"),
       (165, "酉"), (195, "戌"), (225, "亥"), (255, "子"), (285, "丑")]
SEASON_STATE = {  # element states by month-branch season (旺相休囚死)
    "spring": {"Wood": "旺", "Fire": "相", "Water": "休", "Metal": "囚", "Earth": "死"},
    "summer": {"Fire": "旺", "Earth": "相", "Wood": "休", "Water": "囚", "Metal": "死"},
    "autumn": {"Metal": "旺", "Water": "相", "Earth": "休", "Fire": "囚", "Wood": "死"},
    "winter": {"Water": "旺", "Wood": "相", "Metal": "休", "Earth": "囚", "Fire": "死"},
    "earth_month": {"Earth": "旺", "Metal": "相", "Fire": "休", "Wood": "囚", "Water": "死"},
}
BRANCH_SEASON = {"寅": "spring", "卯": "spring", "巳": "summer", "午": "summer", "申": "autumn", "酉": "autumn",
                 "亥": "winter", "子": "winter", "辰": "earth_month", "未": "earth_month", "戌": "earth_month",
                 "丑": "earth_month"}


def ten_god(dm: str, other: str) -> str:
    de, oe = STEM_ELEM[STEMS.index(dm)], STEM_ELEM[STEMS.index(other)]
    same_pol = (STEMS.index(dm) % 2) == (STEMS.index(other) % 2)
    if oe == de:
        return "比肩" if same_pol else "劫财"
    if GEN[de] == oe:
        return "食神" if same_pol else "伤官"
    if CTRL[de] == oe:
        return "偏财" if same_pol else "正财"
    if CTRL[oe] == de:
        return "七杀" if same_pol else "正官"
    if GEN[oe] == de:
        return "偏印" if same_pol else "正印"
    raise ValueError


def ganzhi_index(stem: str, branch: str) -> int:
    s, b = STEMS.index(stem), BRANCHES.index(branch)
    for i in range(60):
        if i % 10 == s and i % 12 == b:
            return i
    raise ValueError


def gz(i: int) -> str:
    return STEMS[i % 10] + BRANCHES[i % 12]


def arithmetic_pillars(local_date, hour_local: float, sun_lon_birth: float, year_after_lichun: int) -> dict:
    """Independent pillar arithmetic (not lunar_python)."""
    # year
    yi = (year_after_lichun - 4) % 60
    # month branch from exact solar longitude
    best = None
    for start, br in JIE:
        d = (sun_lon_birth - start) % 360
        if d < 30:
            best = br
    mb = BRANCHES.index(best)
    # month stem: Yin month stem = ((year stem % 5) * 2 + 2) % 10
    yin_stem = ((yi % 10) % 5 * 2 + 2) % 10
    ms = (yin_stem + (mb - 2) % 12) % 10
    # day: JDN based; (JDN - 11) mod 60, 0 = 甲子
    from convertdate import gregorian as g
    jdn = int(g.to_jd(local_date.year, local_date.month, local_date.day) + 0.5)
    di = (jdn - 11) % 60
    # hour branch: 23-01 = 子
    hb = int(((hour_local + 1) % 24) // 2)
    ds = di % 10
    hs = ((ds % 5) * 2 + hb) % 10
    return {"year": gz(yi), "month": STEMS[ms] + BRANCHES[mb], "day": gz(di), "hour": STEMS[hs] + BRANCHES[hb],
            "jdn": jdn}


def lunar_python_pillars(y, m, d, hh, mm, ss=0) -> dict:
    s = Solar.fromYmdHms(y, m, d, hh, mm, ss)
    l = s.getLunar()
    e = l.getEightChar()
    return {"year": e.getYear(), "month": e.getMonth(), "day": e.getDay(), "hour": e.getTime(),
            "nayin": {"year": e.getYearNaYin(), "month": e.getMonthNaYin(), "day": e.getDayNaYin(),
                      "hour": e.getTimeNaYin()},
            "hidden": {"year": e.getYearHideGan(), "month": e.getMonthHideGan(), "day": e.getDayHideGan(),
                       "hour": e.getTimeHideGan()},
            "lunar_date": str(l), "lunar_month": l.getMonth(), "lunar_day": l.getDay(),
            "_eightchar": e}


PAIRS_STEM_COMBO = {frozenset("甲己"): "Earth", frozenset("乙庚"): "Metal", frozenset("丙辛"): "Water",
                    frozenset("丁壬"): "Wood", frozenset("戊癸"): "Fire"}
STEM_CLASH = [frozenset("甲庚"), frozenset("乙辛"), frozenset("丙壬"), frozenset("丁癸")]
SIX_COMBO = {frozenset("子丑"): "Earth", frozenset("寅亥"): "Wood", frozenset("卯戌"): "Fire",
             frozenset("辰酉"): "Metal", frozenset("巳申"): "Water", frozenset("午未"): "Fire/Earth"}
CLASH = [frozenset(x) for x in ("子午", "丑未", "寅申", "卯酉", "辰戌", "巳亥")]
HARM = [frozenset(x) for x in ("子未", "丑午", "寅巳", "卯辰", "申亥", "酉戌")]
DESTRUCTION = [frozenset(x) for x in ("子酉", "卯午", "辰丑", "未戌", "寅亥", "巳申")]
PUNISH_GROUPS = [("寅巳申", "ungrateful"), ("丑戌未", "bullying"), ("子卯", "uncivil")]
SELF_PUNISH = set("辰午酉亥")
TRINES = {"申子辰": "Water", "亥卯未": "Wood", "寅午戌": "Fire", "巳酉丑": "Metal"}
DIRECTIONAL = {"寅卯辰": "Wood", "巳午未": "Fire", "申酉戌": "Metal", "亥子丑": "Water"}


def interactions(pillars: dict) -> dict:
    names = ["year", "month", "day", "hour"]
    stems = {n: pillars[n][0] for n in names}
    brs = {n: pillars[n][1] for n in names}
    out = {"stem_combinations": [], "stem_clashes": [], "branch_six_combinations": [], "branch_clashes": [],
           "branch_harms": [], "branch_destructions": [], "branch_punishments": [], "three_harmony": [],
           "directional": []}
    for i, a in enumerate(names):
        for b in names[i + 1:]:
            ps = frozenset(stems[a] + stems[b])
            if ps in PAIRS_STEM_COMBO:
                out["stem_combinations"].append({"pillars": [a, b], "stems": stems[a] + stems[b],
                                                 "potential_element": PAIRS_STEM_COMBO[ps],
                                                 "transformation_asserted": False})
            if ps in STEM_CLASH:
                out["stem_clashes"].append({"pillars": [a, b], "stems": stems[a] + stems[b]})
            pb = frozenset(brs[a] + brs[b])
            if pb in SIX_COMBO:
                out["branch_six_combinations"].append({"pillars": [a, b], "branches": brs[a] + brs[b],
                                                       "potential_element": SIX_COMBO[pb],
                                                       "transformation_asserted": False})
            if pb in CLASH:
                out["branch_clashes"].append({"pillars": [a, b], "branches": brs[a] + brs[b]})
            if pb in HARM:
                out["branch_harms"].append({"pillars": [a, b], "branches": brs[a] + brs[b]})
            if pb in DESTRUCTION:
                out["branch_destructions"].append({"pillars": [a, b], "branches": brs[a] + brs[b]})
            if brs[a] == brs[b] and brs[a] in SELF_PUNISH:
                out["branch_punishments"].append({"pillars": [a, b], "type": "self", "branches": brs[a] + brs[b]})
    allb = "".join(brs[n] for n in names)
    for grp, typ in PUNISH_GROUPS:
        present = [c for c in grp if c in allb]
        if (len(grp) == 2 and len(present) == 2) or (len(grp) == 3 and len(present) >= 2):
            out["branch_punishments"].append({"group": grp, "type": typ, "present": present,
                                              "complete": len(present) == len(grp)})
    for grp, el in TRINES.items():
        present = [c for c in grp if c in allb]
        if len(present) >= 2:
            out["three_harmony"].append({"group": grp, "element": el, "present": present,
                                         "complete": len(present) == 3,
                                         "half_includes_center": grp[1] in present})
    for grp, el in DIRECTIONAL.items():
        present = [c for c in grp if c in allb]
        if len(present) >= 2:
            out["directional"].append({"group": grp, "element": el, "present": present, "complete": len(present) == 3})
    return out


def day_master_strength(pillars: dict) -> dict:
    """Declared rule set DM-1 (simplified points method).

    Visible stems (excluding the Day Master) weight 1.0; hidden stems 1.0/0.5/0.3 (main/middle/residual);
    every contribution from the month branch is multiplied by 2 (seasonal command).
    Support = same element as DM + element producing DM. Strong if support share >= 0.5.
    """
    dm = pillars["day"][0]
    de = STEM_ELEM[STEMS.index(dm)]
    resource = [k for k, v in GEN.items() if v == de][0]
    items = []
    for n in ("year", "month", "day", "hour"):
        st, br = pillars[n][0], pillars[n][1]
        if n != "day":
            items.append({"char": st, "pos": f"{n}_stem", "weight": 1.0, "element": STEM_ELEM[STEMS.index(st)]})
        for k, hs in enumerate(HIDDEN[br]):
            w = HIDDEN_WEIGHTS[k] * (2.0 if n == "month" else 1.0)
            items.append({"char": hs, "pos": f"{n}_branch_hidden_{k}", "weight": w,
                          "element": STEM_ELEM[STEMS.index(hs)]})
    sup = sum(i["weight"] for i in items if i["element"] in (de, resource))
    tot = sum(i["weight"] for i in items)
    season = BRANCH_SEASON[pillars["month"][1]]
    state = SEASON_STATE[season][de]
    rooted = [n for n in ("year", "month", "day", "hour") if any(STEM_ELEM[STEMS.index(h)] == de for h in HIDDEN[pillars[n][1]])]
    share = sup / tot
    verdict = "strong" if share >= 0.5 else "weak"
    return {"rule_set": "DM-1 simplified points (declared, not a classical text)", "day_master": dm,
            "day_master_element": de, "resource_element": resource, "support_points": sup, "total_points": tot,
            "support_share": share, "seasonal_state": state, "season": season, "rooted_in_branches": rooted,
            "verdict": verdict, "items": items}


def useful_god(strength: dict, month_branch: str) -> dict:
    de = strength["day_master_element"]
    res = strength["resource_element"]
    output = GEN[de]
    wealth = CTRL[de]
    officer = [k for k, v in CTRL.items() if v == de][0]
    if strength["verdict"] == "weak":
        fa = [res, de]
        unf = [output, wealth, officer]
    else:
        fa = [output, wealth, officer]
        unf = [res, de]
    season = BRANCH_SEASON[month_branch]
    if season == "summer":
        clim_fav, clim_unf, note = ["Water", "Metal"], ["Fire"], "hot season: cool and moisten"
    elif season == "winter":
        clim_fav, clim_unf, note = ["Fire", "Wood"], ["Water"], "cold season: warm"
    else:
        clim_fav, clim_unf, note = [], [], "no strong climate adjustment in this simplified rule"
    agree = sorted(set(fa) & set(clim_fav))
    disagree = sorted((set(fa) & set(clim_unf)) | (set(unf) & set(clim_fav)))
    return {
        "schools": {
            "UG-A strength-balance (扶抑, declared simplified)": {"favorable": fa, "unfavorable": unf,
                                                               "rule": "weak DM -> resource & companion; strong DM -> output, wealth, officer"},
            "UG-B climate adjustment (调候, declared generic seasonal rule; not the full 穷通宝鉴 text)":
                {"favorable": clim_fav, "unfavorable": clim_unf, "rule": note},
        },
        "agreement_favorable": agree, "disagreement": disagree,
        "confidence": "medium" if agree and not disagree else "low",
        "element_roles": {"companion": de, "resource": res, "output": output, "wealth": wealth, "officer": officer},
    }


def da_yun(month_pillar: str, year_stem: str, gender: str, birth_utc: datetime, prev_jie_utc: datetime,
           next_jie_utc: datetime, n: int = 9) -> dict:
    yang_year = STEMS.index(year_stem) % 2 == 0
    forward = (yang_year and gender == "male") or ((not yang_year) and gender == "female")
    delta = (next_jie_utc - birth_utc) if forward else (birth_utc - prev_jie_utc)
    days = delta.total_seconds() / 86400.0
    # Rule DY-A (classical counting): 3 days = 1 year, 1 day = 4 months, 1 shichen (2 h) = 10 days,
    # added as calendar years/months/days to the birth date.
    yrs = int(days // 3)
    rem_months_f = (days - 3 * yrs) * 4.0
    mons = int(rem_months_f)
    extra_days = (rem_months_f - mons) * 30.0
    y_, m_ = birth_utc.year + yrs, birth_utc.month + mons
    while m_ > 12:
        y_, m_ = y_ + 1, m_ - 12
    start_a = birth_utc.replace(year=y_, month=m_) + timedelta(days=extra_days)
    # Rule DY-B: 3 days = 1 tropical year (proportional)
    start_b = birth_utc + timedelta(days=days / 3.0 * 365.2422)
    mi = ganzhi_index(month_pillar[0], month_pillar[1])
    periods = []
    for k in range(1, n + 1):
        idx = (mi + k) % 60 if forward else (mi - k) % 60
        s = start_a + timedelta(days=365.2422 * 10 * (k - 1))
        e = start_a + timedelta(days=365.2422 * 10 * k)
        periods.append({"pillar": gz(idx), "start": s.isoformat(), "end": e.isoformat(),
                        "start_age_years": (s - birth_utc).days / 365.2422})
    return {"direction": "forward" if forward else "reverse", "days_to_jie": days,
            "jie_used": (next_jie_utc if forward else prev_jie_utc).isoformat(),
            "start_rule_DY_A": start_a.isoformat(), "DY_A_offset": {"years": yrs, "months": mons, "days": extra_days}, "start_rule_DY_B": start_b.isoformat(),
            "start_difference_days": abs((start_a - start_b).total_seconds()) / 86400,
            "period_length_years": 10, "periods_based_on": "DY-A start, 10 x 365.2422-day periods",
            "periods": periods}
