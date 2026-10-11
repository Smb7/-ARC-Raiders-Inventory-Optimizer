"""widen item id columns

Revision ID: 0003_widen_item_ids
Revises: 0002_game_data_stations
Create Date: 2026-10-11

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0003_widen_item_ids"
down_revision: str | None = "0002_game_data_stations"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.alter_column("stack_limits", "item_id", existing_type=sa.String(length=64), type_=sa.String(length=128))
    op.alter_column("recipe_ingredients", "item_id", existing_type=sa.String(length=64), type_=sa.String(length=128))
    op.alter_column("recipes", "output_item_id", existing_type=sa.String(length=64), type_=sa.String(length=128))
    op.alter_column("recycling_yields", "source_item_id", existing_type=sa.String(length=64), type_=sa.String(length=128))
    op.alter_column("recycling_yields", "result_item_id", existing_type=sa.String(length=64), type_=sa.String(length=128))
    op.alter_column("items_static", "id", existing_type=sa.String(length=64), type_=sa.String(length=128))


def downgrade() -> None:
    op.alter_column("items_static", "id", existing_type=sa.String(length=128), type_=sa.String(length=64))
    op.alter_column("recycling_yields", "result_item_id", existing_type=sa.String(length=128), type_=sa.String(length=64))
    op.alter_column("recycling_yields", "source_item_id", existing_type=sa.String(length=128), type_=sa.String(length=64))
    op.alter_column("recipes", "output_item_id", existing_type=sa.String(length=128), type_=sa.String(length=64))
    op.alter_column("recipe_ingredients", "item_id", existing_type=sa.String(length=128), type_=sa.String(length=64))
    op.alter_column("stack_limits", "item_id", existing_type=sa.String(length=128), type_=sa.String(length=64))
