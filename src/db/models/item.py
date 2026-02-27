from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime
from sqlalchemy import ForeignKey
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship

from db.models.base import Base


if TYPE_CHECKING:
    from .feed import Feed


class Item(Base):
    __tablename__ = 'items'

    id: Mapped[int] = mapped_column(
        primary_key=True,
        autoincrement=True,
    )
    title: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        unique=True,
    )
    link: Mapped[str] = mapped_column(
        String(2000),
        nullable=False,
        unique=True,
    )
    description: Mapped[str] = mapped_column(
        String(500),
        nullable=True,
        unique=False,
    )
    guid: Mapped[str] = mapped_column(
        String(2000),
        nullable=False,
        unique=True,
        index=True,
    )
    pubDate: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        unique=False,
        index=True,
    )
    feed_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey('feeds.id'),
        unique=False,
    )
    feed: Mapped['Feed'] = relationship(
        'Feed',
        back_populates='items',
        uselist=False,
    )
