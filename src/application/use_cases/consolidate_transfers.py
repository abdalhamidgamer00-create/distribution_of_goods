"""Use case for consolidating transfers and surplus into final logistics reports."""

from datetime import datetime
from src.core.domain.branches.config import get_branches
from src.shared.utils.logging_utils import get_logger
from src.domain.models.entities import Branch as BranchEntity
from src.application.interfaces.repository import DataRepository

logger = get_logger(__name__)

class ConsolidateTransfers:
    """
    Orchestrates the creation of final merged and separate logistics reports.
    Iterates through branches and invokes the combining logic for each.
    """

    def __init__(self, repository: DataRepository):
        self._repository = repository

    def execute(self, **kwargs) -> bool:
        """Processes all branches to generate consolidated logistics files."""
        timestamp_string = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        try:
            total_merged_files = 0
            total_separate_files = 0
            
            branch_list = get_branches()
            logger.info("Consolidating transfers for %d branches...", len(branch_list))
            
            for branch_name in branch_list:
                logger.debug(f"Processing branch: {branch_name}")
                merged_count, separate_count = self.execute_for_branch(
                    BranchEntity(name=branch_name), 
                    timestamp_string
                )
                total_merged_files += merged_count
                total_separate_files += separate_count
            
            self._log_execution_summary(total_merged_files, total_separate_files)
            return (total_merged_files + total_separate_files) > 0
            
        except Exception as e:
            logger.exception(f"ConsolidateTransfers use case failed: {e}")
            return False

    def execute_for_branch(self, branch: BranchEntity, timestamp_string: str) -> tuple:
        """
        Executes the consolidation logic for a specific branch.
        Returns (merged_count, separate_count).
        """
        from src.domain.models.entities import Branch
        from src.domain.services.consolidation_service import ConsolidationEngine
        
        # 1. Load all required data via repository
        # transfers_from: transfers where this branch is the SOURCE
        all_transfers = self._repository.load_transfers()
        transfers_from_branch = [t for t in all_transfers if t.from_branch.name == branch.name]
        
        # surplus: items where this branch has REMAINING SURPLUS (Step 9)
        surplus_items = self._repository.load_remaining_surplus(branch)
        
        if not transfers_from_branch and not surplus_items:
            logger.debug(f"No data to consolidate for branch: {branch.name}")
            return 0, 0

        # 2. Get balances from analytics (Step 6)
        # We need a way to get balances for all branches for these products
        # For now, the engine handles missing balances or we can pre-fetch
        branches_list = [Branch(name=name) for name in get_branches()]
        branch_balances_map = {}
        for b in branches_list:
            stocks = self._repository.load_stock_levels(b)
            branch_balances_map[b.name] = {code: s.balance for code, s in stocks.items()}

        # 3. Use domain engine to combine
        engine = ConsolidationEngine()
        merged_results, separate_results = engine.combine_data(
            branch=branch,
            transfers=transfers_from_branch,
            surplus_items=surplus_items,
            branch_balances=branch_balances_map
        )
        
        # 4. Persist results
        self._repository.save_combined_transfers(
            branch=branch,
            merged_data_list=merged_results,
            separate_data_list=separate_results,
            timestamp_string=timestamp_string
        )
        
        return len(merged_results), len(separate_results)

    def _log_execution_summary(self, merged_count: int, separate_count: int) -> None:
        """Logs a summary of the generation process."""
        logger.info("=" * 50)
        logger.info(f"Generated {merged_count} merged files (CSV + Excel)")
        logger.info(f"Generated {separate_count} separate files (CSV + Excel)")
        logger.info(f"Merged output: data/output/combined_transfers/merged/excel")
        logger.info(f"Separate output: data/output/combined_transfers/separate/excel")
