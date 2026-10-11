from collections import defaultdict

from app.db.models import (
    ItemCategory,
    ItemStatic,
    Recipe,
    RecipeType,
    RecycleContext,
    RecyclingYield,
    User,
    Workbench,
)
from app.schemas.optimize import ChecklistItem, OptimizeResult, YieldPreview
from app.schemas.stash import NormalizedStashItem

REASON_HIDEOUT = "Hideout Need"
REASON_AMMO = "Ammo Essential"
REASON_SEED = "High-Value Seed"
REASON_YIELD = "Yield Value"
REASON_WEIGHT = "Weight Reduction"
REASON_DURABILITY = "Low Durability"
REASON_TRASH = "Vendor Trash"
REASON_EXCESS = "Excess Capacity"
REASON_UNUSABLE = "Unusable Core"

_WORKBENCH_LEVEL = {
    Workbench.SCRAPPY.value: "scrappy_level",
    Workbench.GUNSMITH.value: "gunsmith_level",
    Workbench.GEAR_BENCH.value: "gear_bench_level",
    Workbench.MEDICAL_LAB.value: "medical_lab_level",
    Workbench.EXPLOSIVES_STATION.value: "explosives_station_level",
    Workbench.UTILITY_STATION.value: "utility_station_level",
    Workbench.REFINER.value: "refiner_level",
    Workbench.RESEARCH_STATION.value: "research_station_level",
    Workbench.STASH.value: "stash_level",
}


def hideout_needed_quantities(user: User, recipes: list[Recipe]) -> dict[str, int]:
    needed: dict[str, int] = defaultdict(int)
    for recipe in recipes:
        if recipe.recipe_type != RecipeType.HIDEOUT_UPGRADE or recipe.station is None:
            continue
        attr = _WORKBENCH_LEVEL.get(recipe.station)
        if attr is None:
            continue
        current_level = getattr(user, attr)
        if recipe.station_level != current_level + 1:
            continue
        for ingredient in recipe.ingredients:
            needed[ingredient.item_id] += ingredient.quantity
    return dict(needed)


def _workbench_level(user: User, workbench: str | None) -> int:
    if not workbench:
        return 1
    attr = _WORKBENCH_LEVEL.get(workbench)
    if attr is None:
        return 1
    return int(getattr(user, attr))


def _is_low_durability(item: NormalizedStashItem) -> bool:
    if item.durability is None:
        return False
    if item.category not in {ItemCategory.WEAPON.value, ItemCategory.SHIELD.value}:
        return False
    if item.durability <= 1:
        return item.durability <= 0.1
    return item.durability <= 10


def _keep_reason(
    item: NormalizedStashItem,
    static: ItemStatic | None,
    user: User,
    hideout_needed: dict[str, int],
) -> str | None:
    if item.item_id in hideout_needed:
        return REASON_HIDEOUT
    if static is None:
        return None
    if static.is_ammo_material and user.never_sell_ammo_materials:
        return REASON_AMMO
    if static.is_high_yield_seed and user.keep_high_yield_seeds:
        return REASON_SEED
    return None


def _is_needed_component(result_id: str, keep_ids: set[str], items_by_id: dict[str, ItemStatic]) -> bool:
    if result_id in keep_ids:
        return True
    result = items_by_id.get(result_id)
    if result is None:
        return False
    return result.category == ItemCategory.MATERIAL.value and result.rarity in {
        "blue",
        "purple",
        "orange",
    }


def _recycle_reason(
    item: NormalizedStashItem,
    static: ItemStatic | None,
    user: User,
    keep_ids: set[str],
    yields_by_source: dict[str, list[RecyclingYield]],
    items_by_id: dict[str, ItemStatic],
) -> str | None:
    source_yields = yields_by_source.get(item.item_id, [])
    stash_yields = [row for row in source_yields if row.context == RecycleContext.IN_STASH]
    if stash_yields and any(_is_needed_component(row.result_item_id, keep_ids, items_by_id) for row in stash_yields):
        return REASON_YIELD
    if static is not None and stash_yields:
        yield_weight = sum(row.result_weight for row in stash_yields)
        if static.weight > yield_weight:
            return REASON_WEIGHT
    if user.highlight_low_durability_duplicates and _is_low_durability(item):
        return REASON_DURABILITY
    return None


def _is_unusable_core(static: ItemStatic | None, user: User) -> bool:
    if static is None or static.required_workbench_level is None:
        return False
    return _workbench_level(user, static.required_workbench) < static.required_workbench_level


def _preview_yields(
    item_id: str,
    yields_by_source: dict[str, list[RecyclingYield]],
    items_by_id: dict[str, ItemStatic],
) -> list[YieldPreview]:
    previews: list[YieldPreview] = []
    for row in yields_by_source.get(item_id, []):
        result = items_by_id.get(row.result_item_id)
        previews.append(
            YieldPreview(
                item_id=row.result_item_id,
                name=result.name if result else row.result_item_id,
                quantity=row.quantity,
                context=row.context,
            )
        )
    return previews


def _entry(
    item: NormalizedStashItem,
    quantity: int,
    reason: str,
    yields: list[YieldPreview] | None = None,
) -> ChecklistItem:
    data = item.model_dump()
    data["quantity"] = quantity
    return ChecklistItem(
        **data,
        reason=reason,
        badge=reason,
        yields=yields or [],
    )


def optimize_stash(
    items: list[NormalizedStashItem],
    user: User,
    recipes: list[Recipe],
    yields: list[RecyclingYield],
    stack_limits: dict[str, int],
    items_by_id: dict[str, ItemStatic],
) -> OptimizeResult:
    hideout_needed = hideout_needed_quantities(user, recipes)
    keep_ids = set(hideout_needed)
    keep_ids.update(item_id for item_id, static in items_by_id.items() if static.is_ammo_material and user.never_sell_ammo_materials)
    keep_ids.update(item_id for item_id, static in items_by_id.items() if static.is_high_yield_seed and user.keep_high_yield_seeds)

    yields_by_source: dict[str, list[RecyclingYield]] = defaultdict(list)
    for row in yields:
        yields_by_source[row.source_item_id].append(row)

    keep: list[ChecklistItem] = []
    recycle: list[ChecklistItem] = []
    sell: list[ChecklistItem] = []

    for item in items:
        static = items_by_id.get(item.item_id)
        remaining = item.quantity
        keep_reason = _keep_reason(item, static, user, hideout_needed)
        if keep_reason:
            keep_qty = remaining
            limit = stack_limits.get(item.item_id)
            if limit is not None and keep_qty > limit:
                sell.append(_entry(item, keep_qty - limit, REASON_EXCESS))
                keep_qty = limit
            if keep_qty:
                keep.append(_entry(item, keep_qty, keep_reason))
            continue

        recycle_reason = _recycle_reason(item, static, user, keep_ids, yields_by_source, items_by_id)
        if recycle_reason:
            recycle.append(
                _entry(
                    item,
                    remaining,
                    recycle_reason,
                    _preview_yields(item.item_id, yields_by_source, items_by_id),
                )
            )
            continue

        if _is_unusable_core(static, user):
            sell.append(_entry(item, remaining, REASON_UNUSABLE))
            continue

        sell.append(_entry(item, remaining, REASON_TRASH))

    return OptimizeResult(
        keep=keep,
        recycle=recycle,
        sell=sell,
        scanned_count=len(items),
        total_quantity=sum(item.quantity for item in items),
    )
