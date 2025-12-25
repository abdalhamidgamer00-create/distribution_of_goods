"""Factory for creating data repositories with standard configurations."""

from src.infrastructure.repositories.base.pandas_repository import PandasDataRepository
from src.shared.config.paths import (
    RENAMED_CSV_DIR, ANALYTICS_DIR, SURPLUS_DIR, 
    SHORTAGE_DIR, TRANSFERS_CSV_DIR, TRANSFERS_ROOT_DIR,
    SALES_REPORT_DIR
)


class RepositoryFactory:
    """Centralizes repository initialization logic."""

    @staticmethod
    def create_pandas_repository() -> PandasDataRepository:
        """Creates a PandasDataRepository with default path configuration."""
        return PandasDataRepository(
            input_dir=RENAMED_CSV_DIR,
            output_dir=TRANSFERS_ROOT_DIR,
            surplus_dir=SURPLUS_DIR,
            shortage_dir=SHORTAGE_DIR,
            analytics_dir=ANALYTICS_DIR,
            transfers_dir=TRANSFERS_CSV_DIR,
            sales_analysis_dir=SALES_REPORT_DIR
        )
