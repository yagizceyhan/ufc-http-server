"""
data_store.py — UFC Fighter Mock Database
In-memory veri deposu + aggregation fonksiyonları
Hiçbir dış kütüphane kullanılmamıştır.
"""

# ─────────────────────────────────────────────
# WEIGHT CLASSES
# ─────────────────────────────────────────────
WEIGHT_CLASSES = [
    {"id": 1, "name": "Strawweight",       "limit_lbs": 115},
    {"id": 2, "name": "Flyweight",         "limit_lbs": 125},
    {"id": 3, "name": "Bantamweight",      "limit_lbs": 135},
    {"id": 4, "name": "Featherweight",     "limit_lbs": 145},
    {"id": 5, "name": "Lightweight",       "limit_lbs": 155},
    {"id": 6, "name": "Welterweight",      "limit_lbs": 170},
    {"id": 7, "name": "Middleweight",      "limit_lbs": 185},
    {"id": 8, "name": "Light Heavyweight", "limit_lbs": 205},
    {"id": 9, "name": "Heavyweight",       "limit_lbs": 265},
]

# ─────────────────────────────────────────────
# FIGHTERS
# ─────────────────────────────────────────────
FIGHTERS = [
    {
        "id": 1,
        "name": "Islam Makhachev",
        "nickname": "N/A",
        "nationality": "Russian",
        "weight_class": "Lightweight",
        "age": 32,
        "height_cm": 178,
        "reach_cm": 178,
        "stance": "Southpaw",
        "wins": 26,
        "losses": 1,
        "draws": 0,
        "wins_by_ko": 8,
        "wins_by_sub": 11,
        "wins_by_dec": 7,
        "title_holder": True,
        "rank": 1,
    },
    {
        "id": 2,
        "name": "Jon Jones",
        "nickname": "Bones",
        "nationality": "American",
        "weight_class": "Heavyweight",
        "age": 36,
        "height_cm": 193,
        "reach_cm": 215,
        "stance": "Orthodox",
        "wins": 27,
        "losses": 1,
        "draws": 0,
        "wins_by_ko": 10,
        "wins_by_sub": 7,
        "wins_by_dec": 10,
        "title_holder": True,
        "rank": 1,
    },
    {
        "id": 3,
        "name": "Leon Edwards",
        "nickname": "Rocky",
        "nationality": "British",
        "weight_class": "Welterweight",
        "age": 32,
        "height_cm": 183,
        "reach_cm": 188,
        "stance": "Orthodox",
        "wins": 22,
        "losses": 3,
        "draws": 0,
        "wins_by_ko": 6,
        "wins_by_sub": 3,
        "wins_by_dec": 13,
        "title_holder": True,
        "rank": 1,
    },
    {
        "id": 4,
        "name": "Alex Pereira",
        "nickname": "Poatan",
        "nationality": "Brazilian",
        "weight_class": "Light Heavyweight",
        "age": 36,
        "height_cm": 193,
        "reach_cm": 203,
        "stance": "Orthodox",
        "wins": 11,
        "losses": 2,
        "draws": 0,
        "wins_by_ko": 9,
        "wins_by_sub": 0,
        "wins_by_dec": 2,
        "title_holder": True,
        "rank": 1,
    },
    {
        "id": 5,
        "name": "Dricus du Plessis",
        "nickname": "Stillknocks",
        "nationality": "South African",
        "weight_class": "Middleweight",
        "age": 30,
        "height_cm": 185,
        "reach_cm": 193,
        "stance": "Orthodox",
        "wins": 22,
        "losses": 2,
        "draws": 0,
        "wins_by_ko": 9,
        "wins_by_sub": 7,
        "wins_by_dec": 6,
        "title_holder": True,
        "rank": 1,
    },
    {
        "id": 6,
        "name": "Dustin Poirier",
        "nickname": "The Diamond",
        "nationality": "American",
        "weight_class": "Lightweight",
        "age": 35,
        "height_cm": 175,
        "reach_cm": 182,
        "stance": "Southpaw",
        "wins": 30,
        "losses": 9,
        "draws": 0,
        "wins_by_ko": 14,
        "wins_by_sub": 5,
        "wins_by_dec": 11,
        "title_holder": False,
        "rank": 3,
    },
    {
        "id": 7,
        "name": "Charles Oliveira",
        "nickname": "Do Bronx",
        "nationality": "Brazilian",
        "weight_class": "Lightweight",
        "age": 34,
        "height_cm": 178,
        "reach_cm": 185,
        "stance": "Orthodox",
        "wins": 34,
        "losses": 9,
        "draws": 0,
        "wins_by_ko": 9,
        "wins_by_sub": 21,
        "wins_by_dec": 4,
        "title_holder": False,
        "rank": 2,
    },
    {
        "id": 8,
        "name": "Sean O'Malley",
        "nickname": "Sugar",
        "nationality": "American",
        "weight_class": "Bantamweight",
        "age": 29,
        "height_cm": 178,
        "reach_cm": 180,
        "stance": "Southpaw",
        "wins": 17,
        "losses": 1,
        "draws": 0,
        "wins_by_ko": 12,
        "wins_by_sub": 1,
        "wins_by_dec": 4,
        "title_holder": False,
        "rank": 2,
    },
    {
        "id": 9,
        "name": "Ilia Topuria",
        "nickname": "El Matador",
        "nationality": "Georgian",
        "weight_class": "Featherweight",
        "age": 27,
        "height_cm": 170,
        "reach_cm": 178,
        "stance": "Orthodox",
        "wins": 15,
        "losses": 0,
        "draws": 0,
        "wins_by_ko": 9,
        "wins_by_sub": 4,
        "wins_by_dec": 2,
        "title_holder": True,
        "rank": 1,
    },
    {
        "id": 10,
        "name": "Conor McGregor",
        "nickname": "The Notorious",
        "nationality": "Irish",
        "weight_class": "Lightweight",
        "age": 35,
        "height_cm": 175,
        "reach_cm": 188,
        "stance": "Southpaw",
        "wins": 22,
        "losses": 6,
        "draws": 0,
        "wins_by_ko": 19,
        "wins_by_sub": 1,
        "wins_by_dec": 2,
        "title_holder": False,
        "rank": 15,
    },
    {
        "id": 11,
        "name": "Khamzat Chimaev",
        "nickname": "Borz",
        "nationality": "Swedish",
        "weight_class": "Welterweight",
        "age": 29,
        "height_cm": 186,
        "reach_cm": 190,
        "stance": "Orthodox",
        "wins": 13,
        "losses": 0,
        "draws": 0,
        "wins_by_ko": 5,
        "wins_by_sub": 6,
        "wins_by_dec": 2,
        "title_holder": False,
        "rank": 3,
    },
    {
        "id": 12,
        "name": "Valentina Shevchenko",
        "nickname": "Bullet",
        "nationality": "Kyrgyz",
        "weight_class": "Flyweight",
        "age": 36,
        "height_cm": 165,
        "reach_cm": 168,
        "stance": "Southpaw",
        "wins": 23,
        "losses": 4,
        "draws": 0,
        "wins_by_ko": 7,
        "wins_by_sub": 5,
        "wins_by_dec": 11,
        "title_holder": False,
        "rank": 2,
    },
]

# ─────────────────────────────────────────────
# AGGREGATION FONKSİYONLARI
# ─────────────────────────────────────────────

def get_all_fighters():
    """Tüm dövüşçüleri döner."""
    return FIGHTERS

def get_fighter_by_id(fighter_id: int):
    """ID'ye göre tek dövüşçü döner, bulamazsa None."""
    for f in FIGHTERS:
        if f["id"] == fighter_id:
            return f
    return None

def filter_fighters(weight_class=None, nationality=None, title_holder=None):
    """Verilen kriterlere göre dövüşçüleri filtreler."""
    result = FIGHTERS
    if weight_class:
        result = [f for f in result if f["weight_class"].lower() == weight_class.lower()]
    if nationality:
        result = [f for f in result if f["nationality"].lower() == nationality.lower()]
    if title_holder is not None:
        result = [f for f in result if f["title_holder"] == title_holder]
    return result

def get_summary_stats():
    """Genel istatistik özetini döner."""
    total = len(FIGHTERS)
    total_fights = sum(f["wins"] + f["losses"] + f["draws"] for f in FIGHTERS)
    avg_age = round(sum(f["age"] for f in FIGHTERS) / total, 1)
    avg_reach = round(sum(f["reach_cm"] for f in FIGHTERS) / total, 1)

    ko_rates = []
    for f in FIGHTERS:
        if f["wins"] > 0:
            ko_rates.append(round(f["wins_by_ko"] / f["wins"] * 100, 1))

    return {
        "total_fighters": total,
        "total_fights_recorded": total_fights,
        "title_holders": sum(1 for f in FIGHTERS if f["title_holder"]),
        "average_age": avg_age,
        "average_reach_cm": avg_reach,
        "avg_ko_rate_pct": round(sum(ko_rates) / len(ko_rates), 1),
        "nationalities": len(set(f["nationality"] for f in FIGHTERS)),
        "weight_classes_represented": len(set(f["weight_class"] for f in FIGHTERS)),
    }

def get_top_fighters(metric="wins", limit=5):
    """
    Verilen metriğe göre sıralı top N dövüşçüyü döner.
    metric: 'wins' | 'ko_rate' | 'sub_rate' | 'win_rate'
    """
    def ko_rate(f):
        return f["wins_by_ko"] / f["wins"] if f["wins"] > 0 else 0

    def sub_rate(f):
        return f["wins_by_sub"] / f["wins"] if f["wins"] > 0 else 0

    def win_rate(f):
        total = f["wins"] + f["losses"] + f["draws"]
        return f["wins"] / total if total > 0 else 0

    key_map = {
        "wins":     lambda f: f["wins"],
        "ko_rate":  ko_rate,
        "sub_rate": sub_rate,
        "win_rate": win_rate,
    }

    key_fn = key_map.get(metric, key_map["wins"])
    sorted_fighters = sorted(FIGHTERS, key=key_fn, reverse=True)

    result = []
    for f in sorted_fighters[:limit]:
        result.append({
            "id":         f["id"],
            "name":       f["name"],
            "weight_class": f["weight_class"],
            metric:       round(key_fn(f) * (100 if metric in ("ko_rate", "sub_rate", "win_rate") else 1), 1),
        })
    return result

def get_all_weight_classes():
    """Tüm sıklet kategorilerini döner."""
    return WEIGHT_CLASSES