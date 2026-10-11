import json
import urllib.request
from pathlib import Path

HEADERS = {
    "Accept": "application/json",
    "User-Agent": "arc-raiders-inventory-optimizer-catalog-sync",
}
DATA_DIR = Path(__file__).resolve().parents[1] / "app" / "data"

STATION_MAP = {
    "weapon_bench": "gunsmith",
    "equipment_bench": "gear_bench",
    "med_station": "medical_lab",
    "explosives_bench": "explosives_station",
    "utility_bench": "utility_station",
    "refiner": "refiner",
    "scrappy": "scrappy",
    "research_station": "research_station",
    "stash": "stash",
}

TYPE_CATEGORY = {
    "Basic Material": "material",
    "Topside Material": "material",
    "Refined Material": "material",
    "Nature": "material",
    "Recyclable": "trinket",
    "Trinket": "trinket",
    "Modification": "attachment",
    "Augment": "attachment",
    "Quick Use": "consumable",
    "Shield": "shield",
}

WEAPON_TYPES = {
    "Assault Rifle",
    "Battle Rifle",
    "Pistol",
    "SMG",
    "Shotgun",
    "Sniper Rifle",
    "LMG",
    "Hand Cannon",
    "Special",
}

RARITY_MAP = {
    "Common": "gray",
    "Uncommon": "green",
    "Rare": "blue",
    "Epic": "purple",
    "Legendary": "orange",
}

AMMO_MATERIALS = {"metal_parts", "rubber_parts", "chemicals"}
HIGH_YIELD_SEEDS = {"magnet", "steel_spring"}


def fetch(path: str) -> dict:
    req = urllib.request.Request(f"https://arctracker.io{path}", headers=HEADERS)
    with urllib.request.urlopen(req, timeout=60) as resp:
        return json.loads(resp.read())


def localize(value: object) -> str:
    if isinstance(value, dict):
        return str(value.get("en") or next(iter(value.values()), ""))
    return str(value or "")


def category_for(item_type: str) -> str:
    if item_type in WEAPON_TYPES:
        return "weapon"
    return TYPE_CATEGORY.get(item_type, "trinket")


def main() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    raw_items = fetch("/api/items")["items"]
    hideout = fetch("/api/hideout")["hideoutModules"]

    items = []
    recycling = []
    by_id = {raw["id"]: raw for raw in raw_items}
    for raw in raw_items:
        item_id = raw["id"]
        weight = float(raw.get("weightKg") or 0)
        items.append(
            {
                "id": item_id,
                "name": localize(raw.get("name")),
                "category": category_for(str(raw.get("type") or "")),
                "rarity": RARITY_MAP.get(str(raw.get("rarity") or ""), "gray"),
                "weight": weight,
                "vendor_sell_price": int(raw.get("value") or 0),
                "stack_size": int(raw.get("stackSize") or 1),
                "is_ammo_material": item_id in AMMO_MATERIALS,
                "is_high_yield_seed": item_id in HIGH_YIELD_SEEDS,
            }
        )
        for context, field in (("in_stash", "recyclesInto"), ("in_raid", "salvagesInto")):
            yields = raw.get(field) or {}
            if not isinstance(yields, dict):
                continue
            for result_id, qty in yields.items():
                result = by_id.get(result_id)
                result_weight = float(result.get("weightKg") or 0) * int(qty) if result else 0
                recycling.append(
                    {
                        "source_item_id": item_id,
                        "result_item_id": result_id,
                        "quantity": int(qty),
                        "context": context,
                        "result_weight": round(result_weight, 4),
                    }
                )

    recipes = []
    for source_id, module in hideout.items():
        station = STATION_MAP.get(source_id)
        if station is None:
            continue
        name = localize(module.get("name"))
        for level in module.get("levels") or []:
            ingredients = [
                [row["itemId"], int(row["quantity"])]
                for row in level.get("requirementItemIds") or []
                if row.get("itemId")
            ]
            recipes.append(
                {
                    "label": f"{name} Level {level['level']}",
                    "station": station,
                    "station_level": int(level["level"]),
                    "ingredients": ingredients,
                }
            )

    (DATA_DIR / "items.json").write_text(json.dumps(items, indent=2), encoding="utf-8")
    (DATA_DIR / "hideout_recipes.json").write_text(json.dumps(recipes, indent=2), encoding="utf-8")
    (DATA_DIR / "recycling.json").write_text(json.dumps(recycling, indent=2), encoding="utf-8")
    print(f"items={len(items)} recipes={len(recipes)} recycling={len(recycling)}")


if __name__ == "__main__":
    main()
