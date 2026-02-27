from typing import TYPE_CHECKING

from sqlalchemy import Boolean
from sqlalchemy import String
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship

from db.models.base import Base

if TYPE_CHECKING:
    from .item import Item


class Feed(Base):
    __tablename__ = 'feeds'

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
        default="",
        nullable=False,
        unique=False,
    )
    items: Mapped['Item'] = relationship(
        'Item',
        back_populates='feed',
        uselist=True,
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
    )
