from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.db.models import (
    ItemCategory,
    ItemRarity,
    ItemStatic,
    Recipe,
    RecipeIngredient,
    RecipeType,
    RecycleContext,
    RecyclingYield,
    StackLimit,
    User,
    Workbench,
)
from app.db.seed import seed_static_data


def test_user_defaults(db: Session) -> None:
    user = User()
    db.add(user)
    db.commit()
    db.refresh(user)

    assert user.id is not None
    assert user.scrappy_level == 1
    assert user.gunsmith_level == 0
    assert user.never_sell_ammo_materials is True
    assert user.arc_tracker_token is None


def test_item_and_stack_limit(db: Session) -> None:
    item = ItemStatic(
        id="duct_tape",
        name="Duct Tape",
        category=ItemCategory.MATERIAL,
        rarity=ItemRarity.GRAY,
        weight=0.15,
        vendor_sell_price=40,
    )
    user = User()
    db.add_all([item, user])
    db.flush()
    db.add(StackLimit(user_id=user.id, item_id=item.id, max_stacks=2))
    db.commit()

    stored = db.scalars(select(StackLimit)).one()
    assert stored.max_stacks == 2
    assert stored.item.name == "Duct Tape"


def test_recipe_ingredients_and_recycling_contexts(db: Session) -> None:
    metal = ItemStatic(
        id="metal_parts",
        name="Metal Parts",
        category=ItemCategory.MATERIAL,
        rarity=ItemRarity.GRAY,
        weight=0.2,
        vendor_sell_price=50,
        is_ammo_material=True,
    )
    module = ItemStatic(
        id="broken_arc_module",
        name="Broken Arc Module",
        category=ItemCategory.TRINKET,
        rarity=ItemRarity.BLUE,
        weight=1.5,
        vendor_sell_price=150,
    )
    circuitry = ItemStatic(
        id="arc_circuitry",
        name="Arc Circuitry",
        category=ItemCategory.MATERIAL,
        rarity=ItemRarity.BLUE,
        weight=0.4,
        vendor_sell_price=500,
    )
    db.add_all([metal, module, circuitry])
    db.flush()

    recipe = Recipe(
        output_item_id=None,
        output_qty=0,
        recipe_type=RecipeType.HIDEOUT_UPGRADE,
        station=Workbench.GUNSMITH,
        station_level=2,
        label="Gunsmith Level 2",
        ingredients=[RecipeIngredient(item_id="metal_parts", quantity=20)],
    )
    db.add(recipe)
    db.add_all(
        [
            RecyclingYield(
                source_item_id="broken_arc_module",
                result_item_id="arc_circuitry",
                quantity=2,
                context=RecycleContext.IN_STASH,
                result_weight=0.8,
            ),
            RecyclingYield(
                source_item_id="broken_arc_module",
                result_item_id="arc_circuitry",
                quantity=1,
                context=RecycleContext.IN_RAID,
                result_weight=0.4,
            ),
        ]
    )
    db.commit()

    yields = db.scalars(select(RecyclingYield)).all()
    assert {item.context for item in yields} == {RecycleContext.IN_STASH, RecycleContext.IN_RAID}
    assert recipe.ingredients[0].quantity == 20


def test_unique_recycling_yield(db: Session) -> None:
    source = ItemStatic(
        id="a",
        name="A",
        category=ItemCategory.TRINKET,
        rarity=ItemRarity.GRAY,
        weight=1,
        vendor_sell_price=1,
    )
    result = ItemStatic(
        id="b",
        name="B",
        category=ItemCategory.MATERIAL,
        rarity=ItemRarity.GRAY,
        weight=1,
        vendor_sell_price=1,
    )
    db.add_all([source, result])
    db.flush()
    db.add(
        RecyclingYield(
            source_item_id="a",
            result_item_id="b",
            quantity=1,
            context=RecycleContext.IN_STASH,
            result_weight=1,
        )
    )
    db.commit()
    db.add(
        RecyclingYield(
            source_item_id="a",
            result_item_id="b",
            quantity=2,
            context=RecycleContext.IN_STASH,
            result_weight=1,
        )
    )
    try:
        db.commit()
        raise AssertionError("expected unique constraint")
    except IntegrityError:
        db.rollback()


def test_seed_static_data_is_idempotent(db: Session) -> None:
    seed_static_data(db)
    seed_static_data(db)

    items = db.scalars(select(ItemStatic)).all()
    recipes = db.scalars(select(Recipe)).all()
    yields = db.scalars(select(RecyclingYield)).all()

    assert len(items) == 985
    assert any(item.is_ammo_material for item in items)
    assert any(item.is_high_yield_seed for item in items)
    assert any(item.id == "dog_collar" for item in items)
    assert len(recipes) >= 27
    assert len(yields) >= 1000
