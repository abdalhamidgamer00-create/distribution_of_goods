"""Surplus redistribution - Second round allocation for wasted surplus"""

from time import perf_counter
from src.core.domain.calculations.order_calculator import get_needing_branches_order_for_product
from src.services.splitting.processors.surplus_helpers import calculate_available_surplus
from src.shared.utils.logging_utils import get_logger

logger = get_logger(__name__)


def redistribute_wasted_surplus(
    branches: list,
    branch_data: dict,
    analytics_data: dict,
    all_withdrawals: dict,
    max_withdrawals: int,
    num_products: int,
    balance_limit: float = 30.0
) -> tuple:
    """
    Redistribute wasted surplus from balance limit rule to other eligible branches.
    
    This function runs a second allocation round after the initial distribution.
    It finds surplus that was not allocated due to balance >= limit rule and
    redistributes it to branches that still have capacity (current_balance < limit).
    
    Args:
        branches: List of all branch names
        branch_data: Dictionary of branch dataframes
        analytics_data: Dictionary mapping branch -> (dataframe, withdrawals_list)
        all_withdrawals: Dictionary tracking all withdrawals {(branch, product_idx): amount}
        max_withdrawals: Current maximum number of withdrawals per product
        num_products: Total number of products
        balance_limit: Maximum allowed balance per branch (default: 30.0)
        
    Returns:
        Tuple of (updated_max_withdrawals, timing_seconds)
    """
    logger.info("Starting second redistribution round for wasted surplus...")
    start_time = perf_counter()
    
    redistributed_count = 0
    
    for product_idx in range(num_products):
        # Find branches that still need products and haven't reached the limit
        needing_branches_second_round = []
        
        for branch in branches:
            branch_df = analytics_data[branch][0]
            balance = branch_df.iloc[product_idx]['balance']
            needed = branch_df.iloc[product_idx]['needed_quantity']
            
            # Calculate current balance (original + transfers so far)
            transferred_so_far = 0.0
            withdrawals_list = analytics_data[branch][1]
            if product_idx < len(withdrawals_list):
                for w in withdrawals_list[product_idx]:
                    transferred_so_far += w.get('surplus_from_branch', 0.0)
            
            current_balance = balance + transferred_so_far
            
            # Only consider branches that:
            # 1. Still need the product (needed > 0)
            # 2. Have not received enough in round 1
            # 3. Current balance hasn't reached the limit (current_balance < balance_limit)
            if needed > 0 and current_balance < balance_limit:
                # Calculate remaining needed after first round transfers
                remaining_needed = needed - transferred_so_far
                
                if remaining_needed > 0:
                    # Ensure transfer doesn't push balance over the limit
                    # remaining_capacity = min(what's needed, what can fit without exceeding 15)
                    remaining_capacity = min(remaining_needed, balance_limit - current_balance)
                    avg_sales = branch_df.iloc[product_idx]['avg_sales']
                    needing_branches_second_round.append((
                        branch, avg_sales, current_balance, remaining_capacity
                    ))
        
        # Sort by priority: lowest current_balance first, then highest avg_sales
        needing_branches_second_round.sort(key=lambda x: (x[2], -x[1]))
        
        # Attempt redistribution for each needing branch
        for branch, avg_sales, current_balance, remaining_capacity in needing_branches_second_round:
            if remaining_capacity <= 0:
                continue
            
            # Search for available surplus in all other branches
            for other_branch in branches:
                if other_branch == branch:
                    continue
                
                # Calculate available surplus
                available_surplus = calculate_available_surplus(
                    branch_data, other_branch, product_idx, all_withdrawals
                )
                
                if available_surplus > 0:
                    # Transfer amount = min(available surplus, remaining capacity)
                    transfer_amount = min(available_surplus, remaining_capacity)
                    
                    if transfer_amount > 0:
                        # Record the withdrawal
                        key = (other_branch, product_idx)
                        all_withdrawals[key] = all_withdrawals.get(key, 0.0) + transfer_amount
                        
                        # Add to analytics
                        withdrawals_list = analytics_data[branch][1]
                        if product_idx < len(withdrawals_list):
                            withdrawals_list[product_idx].append({
                                'surplus_from_branch': transfer_amount,
                                'available_branch': other_branch,
                                'surplus_remaining': available_surplus - transfer_amount,
                                'remaining_needed': 0.0
                            })
                            max_withdrawals = max(max_withdrawals, len(withdrawals_list[product_idx]))
                        
                        remaining_capacity -= transfer_amount
                        redistributed_count += 1
                        
                        logger.debug(
                            f"Second round: Transferred {transfer_amount:.2f} of product {product_idx} "
                            f"from {other_branch} to {branch}"
                        )
                        
                        if remaining_capacity <= 0:
                            break
    
    elapsed_time = perf_counter() - start_time
    logger.info(
        f"Second redistribution round completed in {elapsed_time:.2f}s "
        f"({redistributed_count} transfers)"
    )
    
    return max_withdrawals, elapsed_time
