from uuid import UUID

from pydantic import BaseModel, Field

from app.schemas.stash import NormalizedStashItem


class YieldPreview(BaseModel):
    item_id: str
    name: str
    quantity: int
    context: str


class ChecklistItem(NormalizedStashItem):
    reason: str
    badge: str
    yields: list[YieldPreview] = Field(default_factory=list)


class OptimizeResult(BaseModel):
    keep: list[ChecklistItem]
    recycle: list[ChecklistItem]
    sell: list[ChecklistItem]
    scanned_count: int
    total_quantity: int


class OptimizeRequest(BaseModel):
    user_id: UUID


class StackLimitInput(BaseModel):
    item_id: str
    max_stacks: int = Field(ge=0)


class PreferenceUpdate(BaseModel):
    scrappy_level: int | None = Field(default=None, ge=1)
    gunsmith_level: int | None = Field(default=None, ge=0)
    gear_bench_level: int | None = Field(default=None, ge=0)
    medical_lab_level: int | None = Field(default=None, ge=0)
    explosives_station_level: int | None = Field(default=None, ge=0)
    utility_station_level: int | None = Field(default=None, ge=0)
    refiner_level: int | None = Field(default=None, ge=0)
    research_station_level: int | None = Field(default=None, ge=0)
    stash_level: int | None = Field(default=None, ge=0)
    never_sell_ammo_materials: bool | None = None
    keep_high_yield_seeds: bool | None = None
    highlight_low_durability_duplicates: bool | None = None
    stack_limits: list[StackLimitInput] | None = None
