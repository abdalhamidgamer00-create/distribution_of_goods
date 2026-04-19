from dataclasses import dataclass
from src.shared.constants import (
    NEED_COVERAGE_DAYS, 
    SURPLUS_COVERAGE_DAYS, 
    SHORTAGE_COVERAGE_DAYS
)

@dataclass(frozen=True)
class InventoryConfig:
    """Holds user-defined coverage thresholds for inventory calculations."""
    need_days: int = NEED_COVERAGE_DAYS
    surplus_days: int = SURPLUS_COVERAGE_DAYS
    shortage_days: int = SHORTAGE_COVERAGE_DAYS

    @classmethod
    def default(cls) -> 'InventoryConfig':
        """Returns the standard default configuration."""
        return cls()
