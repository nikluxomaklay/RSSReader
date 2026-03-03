import asyncio

from dateutil.parser import parse
from rss_parser import RSSParser
from sqlalchemy.ext.asyncio import async_sessionmaker

from config import Config
from db.repositories.rss import RSSRepository
from helpers import io_get
from services.rss.schemas import FeedDTO
from services.rss.schemas import ItemDTO
from services.rss.xml import FixedImageRSS


class RSSReader:

    def __init__(
        self,
        config: Config,
        session_factory: async_sessionmaker,
    ):
        self.config = config
        self.session_factory = session_factory

    async def run(self, *args, **kwargs):
        read_tasks = []

        while True:
            read_tasks.clear()

            async with self.session_factory() as session:
                for feed in await RSSRepository(session).get_active_feeds():
                    read_tasks.append(
                        asyncio.create_task(self.read_rss(feed)),
                    )

            read_results = await asyncio.gather(*read_tasks)

            for item_cnt, source in read_results:
                if item_cnt:
                    print(f'Read {item_cnt} new items from {source}')

            await asyncio.sleep(self.config.CHECK_INTERVAL)

    async def read_rss(self, feed: FeedDTO):
        xml = await io_get(feed.link)
        if xml:
            rss = RSSParser.parse(xml, schema=FixedImageRSS)
            new_items_cnt = await self.process_result(rss, feed)
            return new_items_cnt, feed
        else:
            return 0, feed

    async def process_result(self, result, feed):
        new_items_cnt = 0
        async with self.session_factory() as session:
            repo = RSSRepository(session)
            items = []
            for item in result.channel.items:
                item_dto = ItemDTO(
                    title=item.title.content,
                    link=item.links[0].content,
                    description=item.description.content[:500],
                    guid=item.guid.content,
                    pubDate=parse(item.pub_date.content),
                )
                items.append(item_dto)

            result = await repo.insert_items(feed, items)
            new_items_cnt += result.rowcount

            await session.commit()

        return new_items_cnt
