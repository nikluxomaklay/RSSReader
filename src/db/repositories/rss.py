from typing import List

from sqlalchemy.ext.asyncio import AsyncSession

from src.db.models.feed import Feed
from src.db.models.item import Item


class RSSRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_feed(self, title: str = None, link: str = None) -> Feed:
        ...

    async def get_all_feeds(self) -> List[Feed]:
        ...

    async def create_feed(self, obj: Feed) -> Feed:
        ...

    async def update_feed(self, obj: Feed) -> Feed:
        ...

    async def delete_feed(self, obj: Feed) -> bool:
        ...

    async def get_item(self, obj: Feed, guid: str = None) -> Item:
        ...

    async def get_items(self, obj: Feed) -> List[Item]:
        ...

    async def get_all_items(self) -> List[Item]:
        ...

    async def create_item(self, obj: Feed, item: Item) -> Item:
        ...

    async def delete_item(self, item: Item) -> bool:
        ...
