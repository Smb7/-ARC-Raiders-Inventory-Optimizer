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
    Workbench,
)

SAMPLE_ITEMS: list[dict] = [
    {
        "id": "metal_parts",
        "name": "Metal Parts",
        "category": ItemCategory.MATERIAL,
        "rarity": ItemRarity.GRAY,
        "weight": 0.2,
        "vendor_sell_price": 50,
        "is_ammo_material": True,
    },
    {
        "id": "magnets",
        "name": "Magnets",
        "category": ItemCategory.MATERIAL,
        "rarity": ItemRarity.GREEN,
        "weight": 0.3,
        "vendor_sell_price": 200,
        "is_high_yield_seed": True,
    },
    {
        "id": "steel_springs",
        "name": "Steel Springs",
        "category": ItemCategory.MATERIAL,
        "rarity": ItemRarity.GREEN,
        "weight": 0.25,
        "vendor_sell_price": 180,
        "is_high_yield_seed": True,
    },
    {
        "id": "duct_tape",
        "name": "Duct Tape",
        "category": ItemCategory.MATERIAL,
        "rarity": ItemRarity.GRAY,
        "weight": 0.15,
        "vendor_sell_price": 40,
    },
    {
        "id": "arc_circuitry",
        "name": "Arc Circuitry",
        "category": ItemCategory.MATERIAL,
        "rarity": ItemRarity.BLUE,
        "weight": 0.4,
        "vendor_sell_price": 500,
    },
    {
        "id": "arc_motion_core",
        "name": "Arc Motion Core",
        "category": ItemCategory.MATERIAL,
        "rarity": ItemRarity.PURPLE,
        "weight": 0.8,
        "vendor_sell_price": 1200,
        "required_workbench": Workbench.REFINER,
        "required_workbench_level": 3,
    },
    {
        "id": "broken_arc_module",
        "name": "Broken Arc Module",
        "category": ItemCategory.TRINKET,
        "rarity": ItemRarity.BLUE,
        "weight": 1.5,
        "vendor_sell_price": 150,
    },
    {
        "id": "vendor_trinket",
        "name": "Tarnished Lighter",
        "category": ItemCategory.TRINKET,
        "rarity": ItemRarity.GRAY,
        "weight": 0.1,
        "vendor_sell_price": 80,
    },
    {
        "id": "extended_mag",
        "name": "Extended Mag",
        "category": ItemCategory.ATTACHMENT,
        "rarity": ItemRarity.GREEN,
        "weight": 0.35,
        "vendor_sell_price": 250,
    },
]


def seed_static_data(session: Session) -> None:
    if session.get(ItemStatic, "metal_parts") is not None:
        return

    session.add_all([ItemStatic(**item) for item in SAMPLE_ITEMS])
    session.flush()

    gunsmith_upgrade = Recipe(
        output_item_id=None,
        output_qty=0,
        recipe_type=RecipeType.HIDEOUT_UPGRADE,
        station=Workbench.GUNSMITH,
        station_level=2,
        label="Gunsmith Level 2",
        ingredients=[
            RecipeIngredient(item_id="metal_parts", quantity=20),
            RecipeIngredient(item_id="steel_springs", quantity=4),
        ],
    )
    magnet_augment = Recipe(
        output_item_id="extended_mag",
        output_qty=1,
        recipe_type=RecipeType.CRAFT,
        station=Workbench.GUNSMITH,
        station_level=1,
        label="Extended Mag",
        ingredients=[RecipeIngredient(item_id="steel_springs", quantity=3)],
    )
    session.add_all([gunsmith_upgrade, magnet_augment])

    session.add_all(
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
    session.commit()
