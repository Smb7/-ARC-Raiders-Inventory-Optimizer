"""add hideout stations and item stack size

Revision ID: 0002_game_data_stations
Revises: 0001_initial_schema
Create Date: 2026-10-11

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0002_game_data_stations"
down_revision: str | None = "0001_initial_schema"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column("users", sa.Column("gear_bench_level", sa.Integer(), nullable=False, server_default="0"))
    op.add_column("users", sa.Column("medical_lab_level", sa.Integer(), nullable=False, server_default="0"))
    op.add_column("users", sa.Column("explosives_station_level", sa.Integer(), nullable=False, server_default="0"))
    op.add_column("users", sa.Column("utility_station_level", sa.Integer(), nullable=False, server_default="0"))
    op.add_column("users", sa.Column("research_station_level", sa.Integer(), nullable=False, server_default="0"))
    op.add_column("users", sa.Column("stash_level", sa.Integer(), nullable=False, server_default="0"))
    op.add_column("items_static", sa.Column("stack_size", sa.Integer(), nullable=False, server_default="1"))


def downgrade() -> None:
    op.drop_column("items_static", "stack_size")
    op.drop_column("users", "stash_level")
    op.drop_column("users", "research_station_level")
    op.drop_column("users", "utility_station_level")
    op.drop_column("users", "explosives_station_level")
    op.drop_column("users", "medical_lab_level")
    op.drop_column("users", "gear_bench_level")
