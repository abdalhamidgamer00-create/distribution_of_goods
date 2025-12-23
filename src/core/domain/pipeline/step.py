"""Pipeline step domain model."""

from dataclasses import dataclass
from typing import Callable, Any

@dataclass(frozen=True)
class Step:
    """Represents a single execution step in the pipeline."""
    id: str
    name: str
    description: str
    function: Callable[..., Any]
