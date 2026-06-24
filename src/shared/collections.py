"""Generic collection helpers to eliminate repeated grouping boilerplate."""

from collections import defaultdict
from typing import Callable, Dict, Hashable, Iterable, List, TypeVar

T = TypeVar("T")


def group_by(
    items: Iterable[T],
    key_func: Callable[[T], Hashable],
) -> Dict[Hashable, List[T]]:
    """Group *items* into lists keyed by *key_func(item)*.

    Replaces the recurring pattern::

        grouped = {}
        for item in items:
            k = some_key(item)
            if k not in grouped:
                grouped[k] = []
            grouped[k].append(item)

    Usage::

        from src.shared.collections import group_by
        pairs = group_by(transfers, lambda t: (t.from_branch.name, t.to_branch.name))
    """
    grouped: Dict[Hashable, List[T]] = defaultdict(list)
    for item in items:
        grouped[key_func(item)].append(item)
    return dict(grouped)
