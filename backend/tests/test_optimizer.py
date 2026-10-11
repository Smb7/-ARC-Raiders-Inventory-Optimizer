from sqlalchemy.orm import Session

from app.db.models import (
    ItemCategory,
    ItemRarity,
    ItemStatic,
    RecycleContext,
    RecyclingYield,
    User,
)
from app.db.seed import seed_static_data
from app.schemas.stash import NormalizedStashItem
from app.services.optimizer import (
    REASON_AMMO,
    REASON_DURABILITY,
    REASON_EXCESS,
    REASON_HIDEOUT,
    REASON_SEED,
    REASON_TRASH,
    REASON_UNUSABLE,
    REASON_WEIGHT,
    REASON_YIELD,
    optimize_stash,
)
from app.db.models import Recipe, StackLimit
from sqlalchemy import select
from sqlalchemy.orm import selectinload


def _item(
    item_id: str,
    quantity: int,
    *,
    category: str = "material",
    durability: float | None = None,
    name: str | None = None,
) -> NormalizedStashItem:
    return NormalizedStashItem(
        item_id=item_id,
        raw_id=item_id,
        name=name or item_id,
        category=category,
        rarity="gray",
        quantity=quantity,
        weight=1,
        vendor_sell_price=1,
        durability=durability,
        known=True,
    )


def _context(db: Session) -> tuple[User, list[Recipe], list[RecyclingYield], dict[str, ItemStatic]]:
    seed_static_data(db)
    user = User(scrappy_level=1, gunsmith_level=0, refiner_level=3)
    db.add(user)
    db.commit()
    recipes = list(db.scalars(select(Recipe).options(selectinload(Recipe.ingredients))).all())
    yields = list(db.scalars(select(RecyclingYield)).all())
    items = {item.id: item for item in db.scalars(select(ItemStatic)).all()}
    return user, recipes, yields, items


def test_keep_hideout_ammo_and_seeds(db: Session) -> None:
    user, recipes, yields, items = _context(db)
    result = optimize_stash(
        [
            _item("metal_parts", 20, name="Metal Parts"),
            _item("rubber_parts", 30, name="Rubber Parts"),
            _item("magnet", 3, name="Magnet"),
            _item("steel_spring", 4, name="Steel Spring"),
        ],
        user,
        recipes,
        yields,
        {},
        items,
    )
    reasons = {row.item_id: row.reason for row in result.keep}
    assert reasons["metal_parts"] == REASON_HIDEOUT
    assert reasons["rubber_parts"] == REASON_HIDEOUT
    assert reasons["magnet"] == REASON_SEED
    assert reasons["steel_spring"] == REASON_SEED
    assert result.sell == []
    assert result.recycle == []


def test_ammo_keep_when_not_next_hideout(db: Session) -> None:
    user, recipes, yields, items = _context(db)
    user.gunsmith_level = 4
    result = optimize_stash([_item("metal_parts", 5)], user, recipes, yields, {}, items)
    assert result.keep[0].reason == REASON_AMMO


def test_recycle_yield_and_weight(db: Session) -> None:
    user, recipes, yields, items = _context(db)
    result = optimize_stash(
        [_item("broken_arc_module", 1, name="Broken Arc Module")],
        user,
        recipes,
        yields,
        {},
        items,
    )
    assert result.recycle[0].reason == REASON_YIELD
    assert {preview.context for preview in result.recycle[0].yields} == {"in_stash", "in_raid"}


def test_recycle_weight_when_yield_not_needed(db: Session) -> None:
    user, recipes, yields, items = _context(db)
    db.add_all(
        [
            ItemStatic(
                id="heavy_scrap",
                name="Heavy Scrap",
                category=ItemCategory.TRINKET,
                rarity=ItemRarity.GRAY,
                weight=4.0,
                vendor_sell_price=5,
            ),
            ItemStatic(
                id="tiny_nugget",
                name="Tiny Nugget",
                category=ItemCategory.MATERIAL,
                rarity=ItemRarity.GRAY,
                weight=0.2,
                vendor_sell_price=1,
            ),
        ]
    )
    db.flush()
    db.add(
        RecyclingYield(
            source_item_id="heavy_scrap",
            result_item_id="tiny_nugget",
            quantity=1,
            context=RecycleContext.IN_STASH,
            result_weight=0.2,
        )
    )
    db.commit()
    items = {item.id: item for item in db.scalars(select(ItemStatic)).all()}
    yields = list(db.scalars(select(RecyclingYield)).all())
    result = optimize_stash(
        [_item("heavy_scrap", 1, category="trinket")],
        user,
        recipes,
        yields,
        {},
        items,
    )
    assert result.recycle[0].reason == REASON_WEIGHT


def test_low_durability_weapon(db: Session) -> None:
    user, recipes, yields, items = _context(db)
    db.add(
        ItemStatic(
            id="rusty_rifle",
            name="Rusty Rifle",
            category=ItemCategory.WEAPON,
            rarity=ItemRarity.GRAY,
            weight=5,
            vendor_sell_price=10,
        )
    )
    db.commit()
    items = {item.id: item for item in db.scalars(select(ItemStatic)).all()}
    result = optimize_stash(
        [_item("rusty_rifle", 1, category="weapon", durability=3, name="Rusty Rifle")],
        user,
        recipes,
        yields,
        {},
        items,
    )
    assert result.recycle[0].reason == REASON_DURABILITY


def test_sell_vendor_trash_excess_and_unusable_core(db: Session) -> None:
    user, recipes, yields, items = _context(db)
    user.refiner_level = 1
    db.add(StackLimit(user_id=user.id, item_id="metal_parts", max_stacks=5))
    db.commit()
    result = optimize_stash(
        [
            _item("metal_parts", 12, name="Metal Parts"),
            _item("vendor_trinket", 1, name="Tarnished Lighter"),
            _item("arc_motion_core", 1, name="Arc Motion Core"),
        ],
        user,
        recipes,
        yields,
        {"metal_parts": 5},
        items,
    )
    sell_reasons = {row.item_id: row.reason for row in result.sell}
    assert sell_reasons["metal_parts"] == REASON_EXCESS
    assert next(row.quantity for row in result.sell if row.item_id == "metal_parts") == 7
    assert next(row.quantity for row in result.keep if row.item_id == "metal_parts") == 5
    assert sell_reasons["vendor_trinket"] == REASON_TRASH
    assert sell_reasons["arc_motion_core"] == REASON_UNUSABLE
