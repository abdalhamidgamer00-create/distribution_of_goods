"""Pandas implementation of the DataRepository facade."""

from typing import List, Dict, Optional
from src.domain.models.entities import (
    Product, Branch, StockLevel, ConsolidatedStock, BranchStock
)
from src.domain.models.distribution import Transfer, DistributionResult
from src.application.ports.repository import DataRepository
from src.shared.constants import BRANCHES
from src.infrastructure.repositories.transfers_persistence import (
    save_step7_transfers, save_step8_split_transfers
)
from src.infrastructure.repositories.surplus_persistence import (
    save_surplus_reports
)
from src.infrastructure.repositories.shortage_persistence import (
    save_shortage_reports
)
from src.infrastructure.repositories.combined_transfers_persistence import (
    save_step11_combined_transfers
)
from src.infrastructure.repositories.artifact_lister import ArtifactLister
from src.infrastructure.repositories.stock_reader import StockReader
from src.infrastructure.repositories.stock_writer import StockWriter
from src.infrastructure.repositories.transfer_reader import TransferReader
from src.infrastructure.repositories.surplus_reader import SurplusReader
from src.infrastructure.cache.data_cache import DataSnapshotCache


class PandasDataRepository(DataRepository):
    """Facade for persistence, delegating to specialized components."""

    def __init__(self, input_dir: str, output_dir: str, **kwargs):
        self._output_dir = output_dir
        self._transfers_dir = kwargs.get('transfers_dir', output_dir)
        self._cache = DataSnapshotCache()
        self._lister = ArtifactLister(output_dir, **kwargs)
        self._reader = StockReader(kwargs.get('analytics_dir', output_dir))
        self._writer = StockWriter(kwargs.get('analytics_dir', output_dir))
        self._surplus = SurplusReader(kwargs.get('surplus_dir', output_dir))
        self._transfers = TransferReader(output_dir)
        self._input_dir = input_dir

    def load_branches(self) -> List[Branch]:
        return [Branch(name=name) for name in BRANCHES]

    def load_products(self) -> List[Product]:
        consolidated = self.load_consolidated_stock()
        return [item.product for item in consolidated]

    def load_consolidated_stock(self) -> List[ConsolidatedStock]:
        from src.shared.utility.file_handler import get_latest_file
        import os
        name = get_latest_file(self._input_dir, ".csv")
        path = os.path.join(self._input_dir, name) if name else None
        return self._reader.load_consolidated_stock(path)

    def load_stock_levels(self, branch: Branch) -> Dict[str, StockLevel]:
        key = f"stock_levels_{branch.name}"
        if not self._cache.has(key):
            self._cache.set(key, self._reader.load_stock_levels(branch.name))
        return self._cache.get(key)

    def load_transfers(self) -> List[Transfer]:
        if not self._cache.has("step7"):
            self._cache.set("step7", self._transfers.walk_for_transfers())
        return self._cache.get("step7")

    def save_branch_stocks(self, branch: Branch, stocks: List[BranchStock]):
        self._writer.save_branch_stocks(branch, stocks)

    def save_transfers(self, transfers: List[Transfer]):
        save_step7_transfers(transfers, self._transfers_dir)

    def save_split_transfers(self, transfers_list, excel_directory):
        from datetime import datetime
        now = datetime.now().strftime("%Y%m%d_%H%M%S")
        save_step8_split_transfers(
            transfers_list, self._transfers_dir, excel_directory, now
        )

    def save_remaining_surplus(self, results: List[DistributionResult]):
        save_surplus_reports(results, self._lister._surplus_directory)

    def save_shortage_report(self, results: List[DistributionResult]):
        save_shortage_reports(results, self._lister._shortage_directory)

    def load_remaining_surplus(self, branch: Branch) -> List[Dict]:
        return self._surplus.load_remaining_surplus(branch.name)

    def save_combined_transfers(
        self, branch, merged_data_list, separate_data_list, timestamp_string
    ):
        save_step11_combined_transfers(
            branch, merged_data_list, separate_data_list, timestamp_string
        )

    def list_outputs(self, category_name, branch_name_filter=None):
        return self._lister.list_outputs(category_name, branch_name_filter)
