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
    gunsmith_level: int | None = Field(default=None, ge=1)
    refiner_level: int | None = Field(default=None, ge=1)
    never_sell_ammo_materials: bool | None = None
    keep_high_yield_seeds: bool | None = None
    highlight_low_durability_duplicates: bool | None = None
    stack_limits: list[StackLimitInput] | None = None
