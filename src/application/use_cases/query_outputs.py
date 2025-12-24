"""Use case for querying generated output artifacts."""

from typing import List, Dict, Optional
from src.application.ports.repository import DataRepository

class QueryOutputs:
    """
    Use case to discover available output files for specific categories.
    """
    def __init__(self, repository: DataRepository):
        self._repository = repository

    def execute(
        self, category: str, branch_name: Optional[str] = None
    ) -> List[Dict]:
        """
        Returns a list of available artifacts for the given category and branch.
        """
        return self._repository.list_outputs(category, branch_name)
