import re
import typing as T
from dataclasses import dataclass, asdict, field
from uuid import UUID, uuid4
from datetime import datetime, UTC

DOMAIN_EVENT_REGISTRY: dict[str, type["DomainEvent"]] = {}


def camel_to_snake(name: str) -> str:
    return re.sub(r"(?<!^)(?=[A-Z])", "_", name).lower()


@dataclass(frozen=True)
class DomainEvent:
    event_id: UUID = field(default_factory=uuid4, kw_only=True)
    event_timestamp: str = field(
        default_factory=lambda: datetime.now(tz=UTC).isoformat(), kw_only=True
    )
    event_type: str = field(default_factory=lambda: "", kw_only=True)

    def __init_subclass__(cls, **kwargs: list[dict[str, T.Any]]) -> None:
        super().__init_subclass__(**kwargs)

        # auto register every event
        DOMAIN_EVENT_REGISTRY[cls.__name__] = cls

    def to_dict(self) -> dict[str, T.Any]:
        data = asdict(self)
        data["event_type"] = camel_to_snake(self.__class__.__name__)
        return data
