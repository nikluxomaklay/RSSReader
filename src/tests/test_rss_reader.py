from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from rss_reader import RSSReader
from services.rss.schemas import FeedDTO, ItemDTO


def make_feed(**kwargs):
    defaults = dict(
        id=1,
        title='Test Feed',
        link='http://example.com/rss',
        description='desc',
        is_active=True,
    )
    defaults.update(kwargs)
    return FeedDTO(**defaults)


def make_rss_item(
    title='Article Title',
    link='http://example.com/article',
    description='Short description',
    guid='guid-123',
    pub_date='Mon, 01 Jan 2024 00:00:00 +0000',
):
    item = MagicMock()
    item.title.content = title
    item.links = [MagicMock(content=link)]
    item.description.content = description
    item.guid.content = guid
    item.pub_date.content = pub_date
    return item


def make_rss_result(items=None):
    result = MagicMock()
    result.channel.items = items if items is not None else [make_rss_item()]
    return result


def make_reader(feeds=None, insert_return=1):
    config = MagicMock()
    config.CHECK_INTERVAL = 60
    session_factory = MagicMock()

    reader = RSSReader(config=config, session_factory=session_factory)
    reader.rss_repo = AsyncMock()
    reader.rss_repo.get_active_feeds.return_value = (
        feeds if feeds is not None else [make_feed()]
    )
    reader.rss_repo.insert_items.return_value = insert_return
    return reader


class TestProcessResult:

    @pytest.mark.asyncio
    async def test_returns_item_count(self):
        reader = make_reader(insert_return=3)
        feed = make_feed()
        result = make_rss_result(
            items=[make_rss_item(), make_rss_item(), make_rss_item()],
        )

        count = await reader.process_result(result, feed)

        assert count == 3

    @pytest.mark.asyncio
    async def test_builds_correct_item_dto(self):
        reader = make_reader(insert_return=1)
        feed = make_feed()
        rss_item = make_rss_item(
            title='My Title',
            link='http://example.com/1',
            description='My description',
            guid='unique-guid',
            pub_date='Tue, 02 Jan 2024 12:00:00 +0000',
        )
        result = make_rss_result(items=[rss_item])

        await reader.process_result(result, feed)

        reader.rss_repo.insert_items.assert_called_once()
        _, items = reader.rss_repo.insert_items.call_args[0]
        assert len(items) == 1
        dto = items[0]
        assert dto.title == 'My Title'
        assert dto.link == 'http://example.com/1'
        assert dto.description == 'My description'
        assert dto.guid == 'unique-guid'
        assert isinstance(dto.pubDate, datetime)

    @pytest.mark.asyncio
    async def test_description_truncated_to_500_chars(self):
        reader = make_reader(insert_return=1)
        feed = make_feed()
        long_description = 'x' * 1000
        rss_item = make_rss_item(description=long_description)
        result = make_rss_result(items=[rss_item])

        await reader.process_result(result, feed)

        _, items = reader.rss_repo.insert_items.call_args[0]
        assert len(items[0].description) == 500

    @pytest.mark.asyncio
    async def test_empty_description_becomes_empty_string(self):
        reader = make_reader(insert_return=1)
        feed = make_feed()
        rss_item = make_rss_item()
        rss_item.description.content = None
        result = make_rss_result(items=[rss_item])

        await reader.process_result(result, feed)

        _, items = reader.rss_repo.insert_items.call_args[0]
        assert items[0].description == ''

    @pytest.mark.asyncio
    async def test_empty_items_list(self):
        reader = make_reader(insert_return=0)
        feed = make_feed()
        result = make_rss_result(items=[])

        count = await reader.process_result(result, feed)

        reader.rss_repo.insert_items.assert_called_once_with(feed, [])
        assert count == 0


class TestReadRss:

    @pytest.mark.asyncio
    async def test_returns_count_and_feed_on_success(self):
        reader = make_reader(insert_return=2)
        feed = make_feed()
        rss_result = make_rss_result(items=[make_rss_item(), make_rss_item()])

        with (
            patch('rss_reader.io_get', new=AsyncMock(return_value='<xml/>')),
            patch('rss_reader.RSSParser.parse', return_value=rss_result),
        ):
            count, returned_feed = await reader.read_rss(feed)

        assert count == 2
        assert returned_feed == feed

    @pytest.mark.asyncio
    async def test_returns_zero_when_xml_is_empty(self):
        reader = make_reader()
        feed = make_feed()

        with patch('rss_reader.io_get', new=AsyncMock(return_value='')):
            count, returned_feed = await reader.read_rss(feed)

        assert count == 0
        assert returned_feed == feed
        reader.rss_repo.insert_items.assert_not_called()

    @pytest.mark.asyncio
    async def test_returns_zero_when_xml_is_none(self):
        reader = make_reader()
        feed = make_feed()

        with patch('rss_reader.io_get', new=AsyncMock(return_value=None)):
            count, returned_feed = await reader.read_rss(feed)

        assert count == 0
        assert returned_feed == feed
        reader.rss_repo.insert_items.assert_not_called()

    @pytest.mark.asyncio
    async def test_uses_fixed_image_rss_schema(self):
        from services.rss.xml import FixedImageRSS

        reader = make_reader(insert_return=1)
        feed = make_feed()
        rss_result = make_rss_result()

        with (
            patch('rss_reader.io_get', new=AsyncMock(return_value='<xml/>')),
            patch(
                'rss_reader.RSSParser.parse',
                return_value=rss_result,
            ) as mock_parse,
        ):
            await reader.read_rss(feed)

        mock_parse.assert_called_once_with('<xml/>', schema=FixedImageRSS)


class TestRun:

    @pytest.mark.asyncio
    async def test_run_processes_all_active_feeds(self):
        feeds = [
            make_feed(id=1, title='Feed 1'), make_feed(id=2, title='Feed 2')
        ]
        reader = make_reader(feeds=feeds, insert_return=0)
        reader.read_rss = AsyncMock(side_effect=[(0, feeds[0]), (1, feeds[1])])

        call_count = 0

        async def fake_sleep(_):
            nonlocal call_count
            call_count += 1
            if call_count >= 1:
                raise StopAsyncIteration

        with patch('rss_reader.asyncio.sleep', side_effect=fake_sleep):
            with pytest.raises(StopAsyncIteration):
                await reader.run()

        assert reader.read_rss.call_count == 2

    @pytest.mark.asyncio
    async def test_run_clears_tasks_each_iteration(self):
        feed = make_feed()
        reader = make_reader(feeds=[feed], insert_return=0)
        reader.read_rss = AsyncMock(return_value=(0, feed))

        iterations = 0

        async def fake_sleep(_):
            nonlocal iterations
            iterations += 1
            if iterations >= 2:
                raise StopAsyncIteration

        with patch('rss_reader.asyncio.sleep', side_effect=fake_sleep):
            with pytest.raises(StopAsyncIteration):
                await reader.run()

        assert reader.read_rss.call_count == 2
        assert reader.rss_repo.get_active_feeds.call_count == 2
