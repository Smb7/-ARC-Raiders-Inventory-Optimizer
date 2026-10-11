from sqlalchemy import select
from sqlalchemy.orm import Session

from app.data.catalog import CATALOG_ITEMS, CRAFT_RECIPES, HIDEOUT_RECIPES, RECYCLING_YIELDS
from app.db.models import ItemStatic, Recipe, RecipeIngredient, RecipeType, RecyclingYield

SAMPLE_ITEMS = CATALOG_ITEMS


def seed_static_data(session: Session) -> None:
    for item in CATALOG_ITEMS:
        existing = session.get(ItemStatic, item["id"])
        if existing is None:
            session.add(ItemStatic(**item))
            continue
        for key, value in item.items():
            if key != "id":
                setattr(existing, key, value)
    session.flush()

    wanted_labels = {spec["label"] for spec in [*HIDEOUT_RECIPES, *CRAFT_RECIPES]}
    for recipe in list(session.scalars(select(Recipe)).all()):
        if recipe.label not in wanted_labels:
            session.delete(recipe)
    session.flush()

    existing_labels = set(session.scalars(select(Recipe.label)).all())
    for spec in HIDEOUT_RECIPES:
        if spec["label"] in existing_labels:
            continue
        session.add(
            Recipe(
                output_item_id=None,
                output_qty=0,
                recipe_type=RecipeType.HIDEOUT_UPGRADE,
                station=spec["station"],
                station_level=spec["station_level"],
                label=spec["label"],
                ingredients=[
                    RecipeIngredient(item_id=item_id, quantity=qty) for item_id, qty in spec["ingredients"]
                ],
            )
        )
    for spec in CRAFT_RECIPES:
        if spec["label"] in existing_labels:
            continue
        session.add(
            Recipe(
                output_item_id=spec["output_item_id"],
                output_qty=spec["output_qty"],
                recipe_type=RecipeType.CRAFT,
                station=spec["station"],
                station_level=spec["station_level"],
                label=spec["label"],
                ingredients=[
                    RecipeIngredient(item_id=item_id, quantity=qty) for item_id, qty in spec["ingredients"]
                ],
            )
        )
    session.flush()

    existing_yields = {
        (row.source_item_id, row.result_item_id, row.context)
        for row in session.scalars(select(RecyclingYield)).all()
    }
    for spec in RECYCLING_YIELDS:
        key = (spec["source_item_id"], spec["result_item_id"], spec["context"])
        if key in existing_yields:
            continue
        session.add(RecyclingYield(**spec))
    session.commit()
