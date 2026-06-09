import sqlalchemy as sa
import sqlalchemy.orm as so

from uuid6 import uuid7
from datetime import datetime

from src.core.config import ENVS
from src.modules.shared.infrastructure import BaseModel

from ...domain.value_objects import ShortURLID


class CODE(BaseModel):
    __tablename__ = "codes"

    code: so.Mapped[str] = so.mapped_column(
        sa.String(ENVS.CONSTANT.SHORT_CODE_LENGTH), primary_key=True
    )  # business rule enforce for 7 chars
    is_used: so.Mapped[bool] = so.mapped_column(default=False)


class URL(BaseModel):
    __tablename__ = "urls"

    short_code: so.Mapped[str] = so.mapped_column(
        sa.String(ENVS.CONSTANT.SHORT_CODE_LENGTH), unique=True
    )
    expires_at: so.Mapped[datetime | None]
    original_url: so.Mapped[str]
    updated_at: so.Mapped[datetime] = so.mapped_column(
        default=lambda: datetime.now(), onupdate=lambda: datetime.now()
    )
    created_at: so.Mapped[datetime] = so.mapped_column(default=lambda: datetime.now())
    id: so.Mapped[ShortURLID] = so.mapped_column(
        primary_key=True, default_factory=lambda: uuid7()
    )
