from typing import List, Optional
from src.domain.models.entities import Branch, NetworkStockState, SurplusEntry
from src.domain.models.distribution import (
    Transfer, LogisticsRecord, ConsolidatedLogisticsReport
)
from src.domain.services.classification.product_classifier import (
    classify_product_type
)


class ConsolidationEngine:
    """Handles the logical combination of transfers and surplus stock."""

    def combine_data(
        self,
        branch: Branch,
        transfers: List[Transfer],
        surplus_entries: List[SurplusEntry],
        network_state: NetworkStockState
    ) -> ConsolidatedLogisticsReport:
        """Combines transfers and surplus into a domain report."""
        records = []
        self._append_normal_transfers(records, branch, transfers, network_state)
        self._append_surplus_records(
            records, branch, surplus_entries, network_state
        )
        
        return ConsolidatedLogisticsReport(
            source_branch=branch,
            records=records
        )

    def _append_normal_transfers(
        self, 
        records: List[LogisticsRecord], 
        branch: Branch, 
        transfers: List[Transfer], 
        network_state: NetworkStockState
    ) -> None:
        """Processes normal transfers and adds them to the record list."""
        for transfer in transfers:
            sender_balance = network_state.get_balance(
                branch.name, transfer.product.code
            )
            receiver_balance = network_state.get_balance(
                transfer.to_branch.name, transfer.product.code
            )
            
            records.append(LogisticsRecord(
                product=transfer.product,
                quantity=transfer.quantity,
                target_branch=transfer.to_branch.name,
                transfer_type='normal',
                sender_balance=sender_balance,
                receiver_balance=receiver_balance,
                category=classify_product_type(transfer.product.name)
            ))

    def _append_surplus_records(
        self, 
        records: List[LogisticsRecord], 
        branch: Branch, 
        surplus_entries: List[SurplusEntry], 
        network_state: NetworkStockState
    ) -> None:
        """Processes surplus entries and adds them to records."""
        # Fix: Administration does not send surplus to itself
        if branch.name == 'administration':
            return

        for surplus in surplus_entries:
            sender_balance = network_state.get_balance(
                branch.name, surplus.product.code
            )
            receiver_balance = network_state.get_balance(
                'administration', surplus.product.code
            )
            
            records.append(LogisticsRecord(
                product=surplus.product,
                quantity=surplus.quantity,
                target_branch='administration',
                transfer_type='surplus',
                sender_balance=sender_balance,
                receiver_balance=receiver_balance,
                category=classify_product_type(surplus.product.name)
            ))
