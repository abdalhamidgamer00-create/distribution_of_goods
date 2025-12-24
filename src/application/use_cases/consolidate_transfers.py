"""Use case for consolidating transfers and surplus reports."""

from datetime import datetime
from src.core.domain.branches.config import get_branches
from src.shared.utils.logging_utils import get_logger
from src.domain.models.entities import Branch as BranchEntity
from src.application.interfaces.repository import DataRepository

logger = get_logger(__name__)


class ConsolidateTransfers:
    """Orchestrates creation of final logistics reports for all branches."""

    def __init__(self, repository: DataRepository):
        self._repository = repository

    def execute(self, **kwargs) -> bool:
        """Processes all branches to generate consolidated logistics files."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        try:
            merged_total, separate_total = self._process_all_branches(timestamp)
            self._log_execution_summary(merged_total, separate_total)
            return (merged_total + separate_total) > 0
        except Exception as error:
            logger.exception(f"ConsolidateTransfers use case failed: {error}")
            return False

    def execute_for_branch(self, branch: BranchEntity, timestamp: str) -> tuple:
        """Executes the consolidation logic for a specific branch."""
        from src.domain.services.consolidation_service import ConsolidationEngine
        
        transfers, surplus = self._load_branch_data(branch)
        if not transfers and not surplus:
            return 0, 0

        balances = self._load_all_branch_balances()
        engine = ConsolidationEngine()
        merged, separate = engine.combine_data(
            branch=branch,
            transfers=transfers,
            surplus_items=surplus,
            branch_balances=balances
        )
        
        self._save_results(branch, merged, separate, timestamp)
        return len(merged), len(separate)

    def _process_all_branches(self, timestamp: str) -> tuple:
        """Iterates through all branches and consolidates their data."""
        merged_total = 0
        separate_total = 0
        branch_names = get_branches()
        
        for name in branch_names:
            m_count, s_count = self.execute_for_branch(
                BranchEntity(name=name), timestamp
            )
            merged_total += m_count
            separate_total += s_count
        return merged_total, separate_total

    def _load_branch_data(self, branch: BranchEntity) -> tuple:
        """Loads transfers and surplus for a specific branch."""
        all_transfers = self._repository.load_transfers()
        transfers = [t for t in all_transfers if t.from_branch.name == branch.name]
        surplus = self._repository.load_remaining_surplus(branch)
        return transfers, surplus

    def _load_all_branch_balances(self) -> dict:
        """Loads current stock balances for all branches."""
        branch_names = get_branches()
        balances_map = {}
        for name in branch_names:
            branch_obj = BranchEntity(name=name)
            stocks = self._repository.load_stock_levels(branch_obj)
            balances_map[name] = {code: s.balance for code, s in stocks.items()}
        return balances_map

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
        logger.info(f"Output: data/output/combined_transfers/")
