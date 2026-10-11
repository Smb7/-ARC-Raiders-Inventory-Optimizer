from __future__ import annotations

import uuid
from datetime import datetime
from enum import StrEnum

from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Integer, String, UniqueConstraint, Uuid, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class ItemCategory(StrEnum):
    MATERIAL = "material"
    WEAPON = "weapon"
    SHIELD = "shield"
    CONSUMABLE = "consumable"
    ATTACHMENT = "attachment"
    TRINKET = "trinket"


class ItemRarity(StrEnum):
    GRAY = "gray"
    GREEN = "green"
    BLUE = "blue"
    PURPLE = "purple"
    ORANGE = "orange"


class RecipeType(StrEnum):
    CRAFT = "craft"
    HIDEOUT_UPGRADE = "hideout_upgrade"


class RecycleContext(StrEnum):
    IN_RAID = "in_raid"
    IN_STASH = "in_stash"


class Workbench(StrEnum):
    SCRAPPY = "scrappy"
    GUNSMITH = "gunsmith"
    GEAR_BENCH = "gear_bench"
    MEDICAL_LAB = "medical_lab"
    EXPLOSIVES_STATION = "explosives_station"
    UTILITY_STATION = "utility_station"
    REFINER = "refiner"
    RESEARCH_STATION = "research_station"
    STASH = "stash"


class User(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    arc_tracker_token: Mapped[str | None] = mapped_column(String(512), nullable=True)
    remember_token: Mapped[bool] = mapped_column(Boolean, default=False)
    scrappy_level: Mapped[int] = mapped_column(Integer, default=1)
    gunsmith_level: Mapped[int] = mapped_column(Integer, default=0)
    gear_bench_level: Mapped[int] = mapped_column(Integer, default=0)
    medical_lab_level: Mapped[int] = mapped_column(Integer, default=0)
    explosives_station_level: Mapped[int] = mapped_column(Integer, default=0)
    utility_station_level: Mapped[int] = mapped_column(Integer, default=0)
    refiner_level: Mapped[int] = mapped_column(Integer, default=0)
    research_station_level: Mapped[int] = mapped_column(Integer, default=0)
    stash_level: Mapped[int] = mapped_column(Integer, default=0)
    never_sell_ammo_materials: Mapped[bool] = mapped_column(Boolean, default=True)
    keep_high_yield_seeds: Mapped[bool] = mapped_column(Boolean, default=True)
    highlight_low_durability_duplicates: Mapped[bool] = mapped_column(Boolean, default=True)

    stack_limits: Mapped[list[StackLimit]] = relationship(back_populates="user", cascade="all, delete-orphan")


class StackLimit(Base):
    __tablename__ = "stack_limits"
    __table_args__ = (UniqueConstraint("user_id", "item_id", name="uq_stack_limits_user_item"),)

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    item_id: Mapped[str] = mapped_column(ForeignKey("items_static.id", ondelete="CASCADE"))
    max_stacks: Mapped[int] = mapped_column(Integer)

    user: Mapped[User] = relationship(back_populates="stack_limits")
    item: Mapped[ItemStatic] = relationship()


class ItemStatic(Base):
    __tablename__ = "items_static"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    name: Mapped[str] = mapped_column(String(128))
    category: Mapped[str] = mapped_column(String(32), index=True)
    rarity: Mapped[str] = mapped_column(String(16), index=True)
    weight: Mapped[float] = mapped_column(Float)
    vendor_sell_price: Mapped[int] = mapped_column(Integer, default=0)
    stack_size: Mapped[int] = mapped_column(Integer, default=1)
    is_ammo_material: Mapped[bool] = mapped_column(Boolean, default=False)
    is_high_yield_seed: Mapped[bool] = mapped_column(Boolean, default=False)
    required_workbench: Mapped[str | None] = mapped_column(String(32), nullable=True)
    required_workbench_level: Mapped[int | None] = mapped_column(Integer, nullable=True)


class Recipe(Base):
    __tablename__ = "recipes"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    output_item_id: Mapped[str | None] = mapped_column(ForeignKey("items_static.id"), nullable=True)
    output_qty: Mapped[int] = mapped_column(Integer, default=1)
    recipe_type: Mapped[str] = mapped_column(String(32), index=True)
    station: Mapped[str | None] = mapped_column(String(32), nullable=True)
    station_level: Mapped[int] = mapped_column(Integer, default=1)
    label: Mapped[str] = mapped_column(String(128))

    ingredients: Mapped[list[RecipeIngredient]] = relationship(
        back_populates="recipe", cascade="all, delete-orphan"
    )
    output_item: Mapped[ItemStatic | None] = relationship()


class RecipeIngredient(Base):
    __tablename__ = "recipe_ingredients"
    __table_args__ = (UniqueConstraint("recipe_id", "item_id", name="uq_recipe_ingredients_recipe_item"),)

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    recipe_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("recipes.id", ondelete="CASCADE"))
    item_id: Mapped[str] = mapped_column(ForeignKey("items_static.id", ondelete="CASCADE"))
    quantity: Mapped[int] = mapped_column(Integer)

    recipe: Mapped[Recipe] = relationship(back_populates="ingredients")
    item: Mapped[ItemStatic] = relationship()


class RecyclingYield(Base):
    __tablename__ = "recycling_yields"
    __table_args__ = (
        UniqueConstraint("source_item_id", "result_item_id", "context", name="uq_recycling_yields_source_result_ctx"),
    )

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    source_item_id: Mapped[str] = mapped_column(ForeignKey("items_static.id", ondelete="CASCADE"))
    result_item_id: Mapped[str] = mapped_column(ForeignKey("items_static.id", ondelete="CASCADE"))
    quantity: Mapped[int] = mapped_column(Integer)
    context: Mapped[str] = mapped_column(String(16), index=True)
    result_weight: Mapped[float] = mapped_column(Float, default=0)

    source_item: Mapped[ItemStatic] = relationship(foreign_keys=[source_item_id])
    result_item: Mapped[ItemStatic] = relationship(foreign_keys=[result_item_id])
