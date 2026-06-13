import typing as T
from dataclasses import asdict

DOMAIN_EVENT_REGISTRY: dict[str, type["DomainEvent"]] = {}


class DomainEvent:
    def __init_subclass__(cls, **kwargs: list[dict[str, T.Any]]):
        super().__init_subclass__(**kwargs)

        # auto register every event
        DOMAIN_EVENT_REGISTRY[cls.__name__] = cls

    def to_dict(self) -> dict[str, T.Any]:
        return asdict(self)  # type: ignore
