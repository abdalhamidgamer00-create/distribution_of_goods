from datetime import datetime
from src.core.domain.branches.config import get_branches
from src.shared.utils.logging_utils import get_logger
from src.domain.models.entities import Branch
from src.application.interfaces.repository import DataRepository
from src.application.services.model_factory import DomainModelFactory
from src.domain.services.consolidation_service import ConsolidationEngine
from src.infrastructure.persistence.presenters import LogisticsPresenter

logger = get_logger(__name__)


class ConsolidateTransfers:
    """Orchestrates creation of final logistics reports for all branches."""

    def __init__(self, repository: DataRepository):
        self._repository = repository
        self._factory = DomainModelFactory()
        self._engine = ConsolidationEngine()
        self._presenter = LogisticsPresenter()

    def execute(self, **kwargs) -> bool:
        """Processes all branches to generate consolidated logistics files."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        try:
            merged_total, separate_total = self._process_all_branches(timestamp)
            self._log_execution_summary(merged_total, separate_total)
            return (merged_total + separate_total) > 0
        except Exception as error:
            logger.exception(f"ConsolidateTransfers execution failed: {error}")
            return False

    def execute_for_branch(self, branch: Branch, timestamp: str) -> tuple:
        """Executes the consolidation logic for a specific branch."""
        transfers, surplus_raw = self._load_branch_input_data(branch)
        if not transfers and not surplus_raw:
            return 0, 0

        network_state = self._factory.create_network_state(
            [Branch(n) for n in get_branches()], 
            self._repository.load_stock_levels
        )
        surplus_entries = self._factory.create_surplus_entries(surplus_raw, branch)
        
        report = self._engine.combine_data(
            branch, transfers, surplus_entries, network_state
        )
        merged, separate = self._presenter.prepare_payloads(report)
        
        self._save_results(branch, merged, separate, timestamp)
        return len(merged), len(separate)

    def _process_all_branches(self, timestamp: str) -> tuple:
        """Iterates through all branches in parallel to consolidate data."""
        from concurrent.futures import ThreadPoolExecutor
        merged_total = 0
        separate_total = 0
        
        with ThreadPoolExecutor() as executor:
            futures = [
                executor.submit(self.execute_for_branch, Branch(name), timestamp)
                for name in get_branches()
            ]
            for future in futures:
                merged_count, separate_count = future.result()
                merged_total += merged_count
                separate_total += separate_count
                
        return merged_total, separate_total

    def _load_branch_input_data(self, branch: Branch) -> tuple:
        """Loads transfers and surplus for a specific branch."""
        all_transfers = self._repository.load_transfers()
        branch_transfers = [t for t in all_transfers if t.from_branch.name == branch.name]
        branch_surplus = self._repository.load_remaining_surplus(branch)
        return branch_transfers, branch_surplus

    def _save_results(self, branch, merged, separate, timestamp) -> None:
        """Persists the consolidated results to the repository."""
        self._repository.save_combined_transfers(
            branch=branch,
            merged_data_list=merged,
            separate_data_list=separate,
            timestamp_string=timestamp
        )

    def _log_execution_summary(self, merged_count: int, separate_count: int) -> None:
        """Logs a summary of the generation process."""
        logger.info("=" * 50)
        logger.info(f"Generated {merged_count} merged files (CSV + Excel)")
        logger.info(f"Generated {separate_count} separate files (CSV + Excel)")
