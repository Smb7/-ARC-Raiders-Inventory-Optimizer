from app.db.models import ItemCategory, ItemRarity, ItemStatic
from app.services.normalize import extract_item_rows, normalize_stash


def _metal() -> ItemStatic:
    return ItemStatic(
        id="metal_parts",
        name="Metal Parts",
        category=ItemCategory.MATERIAL,
        rarity=ItemRarity.GRAY,
        weight=0.2,
        vendor_sell_price=50,
        is_ammo_material=True,
    )


def test_extract_nested_stash_payload() -> None:
    rows = extract_item_rows({"data": {"items": [{"id": "metal_parts", "quantity": 4}]}})
    assert rows == [{"id": "metal_parts", "quantity": 4}]


def test_normalize_maps_known_and_unknown_items() -> None:
    payload = {
        "stash": [
            {"itemId": "metal_parts", "count": 12, "durability": 80},
            {"id": "mystery_core", "qty": 2, "name": "Mystery Core"},
        ]
    }
    result = normalize_stash(payload, {"metal_parts": _metal()})

    assert result.total_quantity == 14
    assert result.unknown_count == 1
    known, unknown = result.items
    assert known.known is True
    assert known.name == "Metal Parts"
    assert known.durability == 80
    assert unknown.known is False
    assert unknown.name == "Mystery Core"


def test_normalize_defaults_quantity_to_one() -> None:
    result = normalize_stash([{"id": "metal_parts"}], {"metal_parts": _metal()})
    assert result.items[0].quantity == 1


def test_normalize_aliases_legacy_item_ids() -> None:
    magnet = ItemStatic(
        id="magnet",
        name="Magnet",
        category=ItemCategory.MATERIAL,
        rarity=ItemRarity.GREEN,
        weight=0.3,
        vendor_sell_price=200,
        is_high_yield_seed=True,
    )
    result = normalize_stash([{"id": "magnets", "quantity": 2}], {"magnet": magnet})
    assert result.items[0].known is True
    assert result.items[0].item_id == "magnet"
    assert result.items[0].raw_id == "magnets"
