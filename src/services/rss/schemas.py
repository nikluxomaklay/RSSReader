from datetime import datetime

from pydantic import BaseModel
from pydantic import ConfigDict


class FeedDTO(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int | None = None
    title: str
    link: str
    description: str
    is_active: bool


class ItemDTO(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int | None = None
    title: str
    link: str
    description: str
    guid: str
    pubDate: datetime
    feed: FeedDTO | None = None
