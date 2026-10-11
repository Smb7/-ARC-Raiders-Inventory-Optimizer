from typing import Any

from app.data.catalog import ITEM_ALIASES
from app.db.models import ItemStatic
from app.schemas.stash import NormalizedStash, NormalizedStashItem

_ID_KEYS = ("id", "itemId", "item_id", "itemID")
_QTY_KEYS = ("quantity", "qty", "count", "amount", "stackSize")
_DURABILITY_KEYS = ("durability", "durabilityPercent", "condition")
_COLLECTION_KEYS = ("items", "stash", "inventory", "data")


def extract_item_rows(payload: Any) -> list[dict[str, Any]]:
    if isinstance(payload, list):
        return [row for row in payload if isinstance(row, dict)]
    if isinstance(payload, dict):
        for key in _COLLECTION_KEYS:
            if key in payload:
                return extract_item_rows(payload[key])
    return []


def _first(row: dict[str, Any], keys: tuple[str, ...]) -> Any | None:
    for key in keys:
        if key in row and row[key] is not None:
            return row[key]
    return None


def normalize_stash(payload: Any, items_by_id: dict[str, ItemStatic]) -> NormalizedStash:
    normalized: list[NormalizedStashItem] = []
    unknown_count = 0

    for row in extract_item_rows(payload):
        raw_id = _first(row, _ID_KEYS)
        if raw_id is None:
            continue
        raw_id_str = str(raw_id)
        item_id = ITEM_ALIASES.get(raw_id_str, raw_id_str)
        quantity_raw = _first(row, _QTY_KEYS)
        quantity = int(quantity_raw) if quantity_raw is not None else 1
        durability_raw = _first(row, _DURABILITY_KEYS)
        durability = float(durability_raw) if durability_raw is not None else None

        static = items_by_id.get(item_id)
        if static is None:
            unknown_count += 1
            normalized.append(
                NormalizedStashItem(
                    item_id=item_id,
                    raw_id=raw_id_str,
                    name=str(row.get("name") or item_id),
                    category="unknown",
                    rarity="unknown",
                    quantity=quantity,
                    weight=0,
                    vendor_sell_price=0,
                    durability=durability,
                    known=False,
                )
            )
            continue

        normalized.append(
            NormalizedStashItem(
                item_id=static.id,
                raw_id=raw_id_str,
                name=static.name,
                category=static.category,
                rarity=static.rarity,
                quantity=quantity,
                weight=static.weight,
                vendor_sell_price=static.vendor_sell_price,
                durability=durability,
                known=True,
            )
        )

    return NormalizedStash(
        items=normalized,
        unknown_count=unknown_count,
        total_quantity=sum(item.quantity for item in normalized),
    )
