import json
from pathlib import Path

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models import ItemStatic, Recipe, RecipeIngredient, RecipeType, RecyclingYield

DATA_DIR = Path(__file__).resolve().parents[1] / "data"


def _load(name: str) -> list:
    return json.loads((DATA_DIR / name).read_text(encoding="utf-8"))


CATALOG_ITEMS: list[dict] = _load("items.json")
SAMPLE_ITEMS = CATALOG_ITEMS


def seed_static_data(session: Session) -> None:
    items = _load("items.json")
    recipes = [row for row in _load("hideout_recipes.json") if row.get("ingredients")]
    yields = _load("recycling.json")
    item_ids = {row["id"] for row in items}

    for item in items:
        existing = session.get(ItemStatic, item["id"])
        if existing is None:
            session.add(ItemStatic(**item))
            continue
        for key, value in item.items():
            if key != "id":
                setattr(existing, key, value)
    session.flush()

    wanted_labels = {spec["label"] for spec in recipes}
    for recipe in list(session.scalars(select(Recipe)).all()):
        if recipe.label not in wanted_labels:
            session.delete(recipe)
    session.flush()

    existing_labels = set(session.scalars(select(Recipe.label)).all())
    for spec in recipes:
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
                    RecipeIngredient(item_id=item_id, quantity=qty)
                    for item_id, qty in spec["ingredients"]
                    if item_id in item_ids
                ],
            )
        )
    session.flush()

    existing_yields = {
        (row.source_item_id, row.result_item_id, row.context)
        for row in session.scalars(select(RecyclingYield)).all()
    }
    for spec in yields:
        if spec["source_item_id"] not in item_ids or spec["result_item_id"] not in item_ids:
            continue
        key = (spec["source_item_id"], spec["result_item_id"], spec["context"])
        if key in existing_yields:
            continue
        session.add(RecyclingYield(**spec))
    session.commit()
