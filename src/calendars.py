"""Maya calendar (date-based) and Tibetan element-animal year (limited overlay)."""
from __future__ import annotations

from convertdate import gregorian, mayan

TZOLKIN = ["Imix", "Ik'", "Ak'b'al", "K'an", "Chikchan", "Kimi", "Manik'", "Lamat", "Muluk", "Ok",
           "Chuwen", "Eb'", "B'en", "Ix", "Men", "K'ib'", "Kab'an", "Etz'nab'", "Kawak", "Ajaw"]
HAAB = ["Pop", "Wo'", "Sip", "Sotz'", "Sek", "Xul", "Yaxk'in", "Mol", "Ch'en", "Yax", "Sak'", "Keh",
        "Mak", "K'ank'in", "Muwan", "Pax", "K'ayab", "Kumk'u", "Wayeb'"]


def maya(y: int, m: int, d: int, correlation: int = 584283) -> dict:
    # Primary: convertdate
    lc = mayan.from_gregorian(y, m, d)
    jd_mid = gregorian.to_jd(y, m, d)
    tz = mayan.to_tzolkin(jd_mid)
    hb = mayan.to_haab(jd_mid)
    rt = mayan.to_gregorian(*lc)
    # Independent arithmetic (GMT correlation constant as JDN of 13.0.0.0.0 4 Ajaw 8 Kumk'u)
    jdn = int(gregorian.to_jd(y, m, d) + 0.5)
    days = jdn - correlation
    b, r = divmod(days, 144000)
    k, r = divmod(r, 7200)
    t, r = divmod(r, 360)
    u, ki = divmod(r, 20)
    num = (days + 3) % 13 + 1
    name = TZOLKIN[(days + 19) % 20]
    hpos = (days + 348) % 365
    hm, hd = divmod(hpos, 20)
    indep = {"long_count": [b, k, t, u, ki], "tzolkin": [num, name], "haab": [hd, HAAB[hm]]}
    # independent round trip
    back = b * 144000 + k * 7200 + t * 360 + u * 20 + ki + correlation
    back_greg = gregorian.from_jd(back)  # JDN == JD at noon
    return {
        "correlation_constant": correlation, "correlation_name": "GMT (Goodman-Martinez-Thompson)",
        "jdn": jdn, "days_since_creation": days,
        "primary_engine": "convertdate.mayan (EPOCH = %s, i.e. GMT 584283 as JDN)" % mayan.EPOCH,
        "primary": {"long_count": list(lc), "tzolkin": list(tz), "haab": list(hb), "round_trip": list(rt)},
        "independent_arithmetic": indep,
        "independent_round_trip": list(back_greg),
        "calendar_round": f"{num} {name} {hd} {HAAB[hm]}",
        "long_count_str": ".".join(str(x) for x in [b, k, t, u, ki]),
    }


ELEM_TIB = ["Wood", "Wood", "Fire", "Fire", "Earth", "Earth", "Iron", "Iron", "Water", "Water"]
ANIMALS = ["Mouse", "Ox", "Tiger", "Rabbit", "Dragon", "Snake", "Horse", "Sheep", "Monkey", "Bird", "Dog", "Pig"]


def tibetan_year(gregorian_year_of_losar: int) -> dict:
    """Element-animal-gender for the Tibetan year that begins at Losar in the given Gregorian year."""
    i = (gregorian_year_of_losar - 4) % 60  # 0 = Wood-Mouse (= Chinese Jia-Zi)
    rab_year = (gregorian_year_of_losar - 1027) % 60 + 1  # Rabjung cycles from 1027 (Fire-Rabbit = year 1)
    rab_cycle = (gregorian_year_of_losar - 1027) // 60 + 1
    return {"element": ELEM_TIB[i % 10], "animal": ANIMALS[i % 12],
            "gender": "male" if i % 2 == 0 else "female",
            "sexagenary_index_0_wood_mouse": i, "rabjung_cycle": rab_cycle, "rabjung_year": rab_year}
