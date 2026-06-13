import typing as T
from dataclasses import dataclass, asdict


@dataclass
class AggregateRoot:
    def convert_to_dict(self, exclude_none_values: bool) -> dict[str, T.Any]:
        data = asdict(self)
        data.pop("events", None)
        if exclude_none_values:
            return {k: v for k, v in data.items() if v is not None}
        return data
