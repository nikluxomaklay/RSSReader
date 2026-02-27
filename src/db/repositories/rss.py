from typing import List

from sqlalchemy.dialects.postgresql import insert
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from db.models.feed import Feed
from db.models.item import Item
from services.rss.schemas import FeedDTO
from services.rss.schemas import ItemDTO


class RSSRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_feed(self, title: str = None, link: str = None) -> Feed:
        ...

    async def get_active_feeds(self) -> List[FeedDTO]:
        result = (await self._session.execute(
            select(Feed).where(Feed.is_active == True)
        )).scalars().all()
        return [FeedDTO.model_validate(model) for model in result]

    async def get_all_feeds(self) -> List[Feed]:
        ...

    def add_feed(self, obj: Feed):
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

    def add_item(self, obj: FeedDTO, item: ItemDTO):
        item_dump = item.model_dump()
        item_dump.pop('feed', None)
        self._session.add(
            Item(feed_id=obj.id, **item_dump),
        )

    async def insert_items(self, obj: FeedDTO, items: List[ItemDTO]):
        prepared_items = []
        for item in items:
            prepared_item = item.model_dump()
            prepared_item['feed_id'] = obj.id
            prepared_item.pop('feed', None)
            prepared_item.pop('id', None)
            prepared_items.append(prepared_item)
        upsert = insert(Item).values(
            prepared_items,
        ).on_conflict_do_nothing(index_elements=['guid'])
        return await self._session.execute(upsert)

    async def delete_item(self, item: Item) -> bool:
        ...
