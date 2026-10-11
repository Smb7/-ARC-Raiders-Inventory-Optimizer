"""initial schema

Revision ID: 0001_initial_schema
Revises:
Create Date: 2026-10-11

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0001_initial_schema"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "items_static",
        sa.Column("id", sa.String(length=64), nullable=False),
        sa.Column("name", sa.String(length=128), nullable=False),
        sa.Column("category", sa.String(length=32), nullable=False),
        sa.Column("rarity", sa.String(length=16), nullable=False),
        sa.Column("weight", sa.Float(), nullable=False),
        sa.Column("vendor_sell_price", sa.Integer(), nullable=False),
        sa.Column("is_ammo_material", sa.Boolean(), nullable=False),
        sa.Column("is_high_yield_seed", sa.Boolean(), nullable=False),
        sa.Column("required_workbench", sa.String(length=32), nullable=True),
        sa.Column("required_workbench_level", sa.Integer(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_items_static_category"), "items_static", ["category"])
    op.create_index(op.f("ix_items_static_rarity"), "items_static", ["rarity"])

    op.create_table(
        "users",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("arc_tracker_token", sa.String(length=512), nullable=True),
        sa.Column("remember_token", sa.Boolean(), nullable=False),
        sa.Column("scrappy_level", sa.Integer(), nullable=False),
        sa.Column("gunsmith_level", sa.Integer(), nullable=False),
        sa.Column("refiner_level", sa.Integer(), nullable=False),
        sa.Column("never_sell_ammo_materials", sa.Boolean(), nullable=False),
        sa.Column("keep_high_yield_seeds", sa.Boolean(), nullable=False),
        sa.Column("highlight_low_durability_duplicates", sa.Boolean(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "stack_limits",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.Column("item_id", sa.String(length=64), nullable=False),
        sa.Column("max_stacks", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(["item_id"], ["items_static.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("user_id", "item_id", name="uq_stack_limits_user_item"),
    )

    op.create_table(
        "recipes",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("output_item_id", sa.String(length=64), nullable=True),
        sa.Column("output_qty", sa.Integer(), nullable=False),
        sa.Column("recipe_type", sa.String(length=32), nullable=False),
        sa.Column("station", sa.String(length=32), nullable=True),
        sa.Column("station_level", sa.Integer(), nullable=False),
        sa.Column("label", sa.String(length=128), nullable=False),
        sa.ForeignKeyConstraint(["output_item_id"], ["items_static.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_recipes_recipe_type"), "recipes", ["recipe_type"])

    op.create_table(
        "recipe_ingredients",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("recipe_id", sa.Uuid(), nullable=False),
        sa.Column("item_id", sa.String(length=64), nullable=False),
        sa.Column("quantity", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(["item_id"], ["items_static.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["recipe_id"], ["recipes.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("recipe_id", "item_id", name="uq_recipe_ingredients_recipe_item"),
    )

    op.create_table(
        "recycling_yields",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("source_item_id", sa.String(length=64), nullable=False),
        sa.Column("result_item_id", sa.String(length=64), nullable=False),
        sa.Column("quantity", sa.Integer(), nullable=False),
        sa.Column("context", sa.String(length=16), nullable=False),
        sa.Column("result_weight", sa.Float(), nullable=False),
        sa.ForeignKeyConstraint(["result_item_id"], ["items_static.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["source_item_id"], ["items_static.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "source_item_id",
            "result_item_id",
            "context",
            name="uq_recycling_yields_source_result_ctx",
        ),
    )
    op.create_index(op.f("ix_recycling_yields_context"), "recycling_yields", ["context"])


def downgrade() -> None:
    op.drop_index(op.f("ix_recycling_yields_context"), table_name="recycling_yields")
    op.drop_table("recycling_yields")
    op.drop_table("recipe_ingredients")
    op.drop_index(op.f("ix_recipes_recipe_type"), table_name="recipes")
    op.drop_table("recipes")
    op.drop_table("stack_limits")
    op.drop_table("users")
    op.drop_index(op.f("ix_items_static_rarity"), table_name="items_static")
    op.drop_index(op.f("ix_items_static_category"), table_name="items_static")
    op.drop_table("items_static")
