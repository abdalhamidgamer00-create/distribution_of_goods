from typing import List, Dict, Optional, Tuple
from src.domain.models.entities import StockLevel
from src.shared.constants import PRIORITY_WEIGHTS


# =============================================================================
# PUBLIC API
# =============================================================================

def get_needing_branches_ordered_by_priority(
    branch_stocks: Dict[str, StockLevel]
) -> List[str]:
    """Returns branch names ordered by their weighted priority score."""
    needing_branches_with_scores = _collect_needing_branches_with_scores(
        branch_stocks
    )
    # Sort by score descending
    needing_branches_with_scores.sort(key=lambda item: -item[1])
    return [branch_name for branch_name, score in needing_branches_with_scores]


def get_surplus_sources_ordered_for_product(
    source_branch_name: str,
    all_branch_stocks: Dict[str, StockLevel],
    existing_withdrawals: Optional[Dict[Tuple[str, int], float]] = None
) -> List[str]:
    """Returns order of branches to search for available surplus."""
    if existing_withdrawals is None:
        existing_withdrawals = {}
    
    surplus_info = _collect_available_surplus_info(
        source_branch_name, all_branch_stocks, existing_withdrawals
    )
    # Sort by surplus desc, then balance desc, then average_daily_sales asc
    surplus_info.sort(key=lambda item: (-item[1], -item[2], item[3]))
    return [branch_name for branch_name, *metrics in surplus_info]


# =============================================================================
# PRIVATE HELPERS
# =============================================================================

def _calculate_priority_score(stock: StockLevel) -> float:
    """Calculates a weighted priority score for a branch's stock status."""
    # Avoid division by zero with a small smoothing factor
    inverse_balance_score = 1.0 / (stock.balance + 0.1)
    return (
        PRIORITY_WEIGHTS["balance"] * inverse_balance_score +
        PRIORITY_WEIGHTS["needed"] * stock.needed +
        PRIORITY_WEIGHTS["average_daily_sales"] * stock.average_daily_sales
    )


def _collect_needing_branches_with_scores(
    branch_stocks: Dict[str, StockLevel]
) -> List[Tuple[str, float]]:
    """Collects branches that actually need products along with their scores."""
    results = []
    for branch_name, stock in branch_stocks.items():
        if stock.needed > 0:
            score = _calculate_priority_score(stock)
            results.append((branch_name, score))
    return results


def _collect_available_surplus_info(
    exclude_branch: str,
    all_branch_stocks: Dict[str, StockLevel],
    withdrawals: Dict
) -> List[Tuple]:
    """Gathers surplus metrics from all branches except the excluded one."""
    surplus_list = []
    for branch_name, stock in all_branch_stocks.items():
        if branch_name == exclude_branch or stock.surplus <= 0:
            continue
            
        # Simplified: we assume product context is managed by caller 
        # as we are now passing specific StockLevel objects
        surplus_list.append((
            branch_name, 
            stock.surplus, 
            stock.balance, 
            stock.average_daily_sales
        ))
    return surplus_list
