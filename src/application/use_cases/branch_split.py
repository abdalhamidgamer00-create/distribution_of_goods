"""Use case for splitting data by branch."""

from typing import Dict, List
from src.application.interfaces.repository import DataRepository
from src.domain.services.branch_service import BranchSplitter


class SplitDataByBranch:
    """
    Orchestrates the process of splitting consolidated data into
    branch-specific records and saving them.
    """

    def __init__(
        self,
        repository: DataRepository,
        splitter: BranchSplitter
    ):
        self._repository = repository
        self._splitter = splitter

    def execute(self) -> None:
        """
        Loads consolidated data, splits it using the domain service,
        and persists the results for each branch.
        """
        branches = self._repository.load_branches()
        consolidated_data = self._repository.load_consolidated_stock()
        
        split_results = self._splitter.split_by_branch(
            consolidated_data, branches
        )
        
        for branch in branches:
            if branch.name in split_results:
                self._repository.save_branch_stocks(
                    branch, split_results[branch.name]
                )
