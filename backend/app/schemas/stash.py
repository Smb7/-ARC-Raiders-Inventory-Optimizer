from pydantic import BaseModel, Field


class NormalizedStashItem(BaseModel):
    item_id: str
    raw_id: str
    name: str
    category: str
    rarity: str
    quantity: int = Field(ge=0)
    weight: float
    vendor_sell_price: int
    durability: float | None = None
    known: bool


class NormalizedStash(BaseModel):
    items: list[NormalizedStashItem]
    unknown_count: int
    total_quantity: int
