from sqlalchemy import BigInteger
from sqlalchemy.orm import Mapped, mapped_column
from core.models.base import Base


class User(Base):
    tg_id: Mapped[int] = mapped_column(BigInteger, unique=True, nullable=False)
    wins: Mapped[int]
    losses: Mapped[int]
    draws: Mapped[int]
