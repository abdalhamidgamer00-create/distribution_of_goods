"""Proportional allocation calculations"""

import pandas as pd
import math


def calculate_proportional_allocations_vectorized(branch_data: dict, branches: list) -> dict:
    """
    Vectorized proportional allocation across all products.
    Using floor to ensure whole numbers
    
    Args:
        branch_data: Dictionary of branch dataframes.
        branches: Ordered list of branches.
    
    Returns:
        Dict mapping product index -> {branch: allocated_amount} (all as integers)
    """
    if not branch_data:
        return {}
    
    # Extract additional data for weighted scoring
    avg_sales_df = pd.DataFrame({
        branch: branch_data[branch]['avg_sales'].astype(float)
        for branch in branches
    })
    balance_df = pd.DataFrame({
        branch: branch_data[branch]['balance'].astype(float)
        for branch in branches
    })
    
    needed_df = pd.DataFrame({
        branch: branch_data[branch]['needed_quantity'].astype(float)
        for branch in branches
    })
    surplus_df = pd.DataFrame({
        branch: branch_data[branch]['surplus_quantity'].astype(float)
        for branch in branches
    })
    
    total_needed = needed_df.clip(lower=0).sum(axis=1)
    total_surplus = surplus_df.clip(lower=0).sum(axis=1)
    needs_mask = (total_needed > 0) & (total_surplus > 0) & (total_surplus < total_needed)
    
    # Allocation weights (approved by user)
    AVG_SALES_WEIGHT = 0.10  # 10% - نشاط الفرع
    NEEDED_WEIGHT = 0.30     # 30% - الاحتياج
    BALANCE_WEIGHT = 0.60    # 60% - أولوية قصوى للرصيد المنخفض
    
    allocations = {}
    for idx in total_needed[needs_mask].index:
        total_needed_value = total_needed.loc[idx]
        if total_needed_value <= 0:
            continue
        
        total_surplus_value = total_surplus.loc[idx]
        
        # Calculate weighted scores for each branch
        # Higher score = higher priority
        
        # Component 1: avg_sales (10%) - higher is better
        avg_sales_scores = avg_sales_df.loc[idx].clip(lower=0)
        
        # Component 2: needed (30%) - higher is better
        needed_scores = needed_df.loc[idx].clip(lower=0)
        
        # Component 3: inverse balance (60%) - lower balance = higher score
        # Add small epsilon to avoid division by zero
        inverse_balance_scores = 1.0 / (balance_df.loc[idx] + 0.1)
        
        # Normalize each component (0 to 1 range)
        def normalize(series):
            min_val = series.min()
            max_val = series.max()
            if max_val - min_val == 0:
                return pd.Series([1.0] * len(series), index=series.index)
            return (series - min_val) / (max_val - min_val)
        
        avg_sales_norm = normalize(avg_sales_scores)
        needed_norm = normalize(needed_scores)
        balance_norm = normalize(inverse_balance_scores)
        
        # Calculate weighted total scores
        total_scores = (
            AVG_SALES_WEIGHT * avg_sales_norm +
            NEEDED_WEIGHT * needed_norm +
            BALANCE_WEIGHT * balance_norm
        )
        
        # Calculate proportions based on scores
        # Only consider branches with needed > 0
        needing_mask = needed_df.loc[idx] > 0
        total_scores_sum = total_scores[needing_mask].sum()
        
        if total_scores_sum <= 0:
            # Fallback to simple proportion if scores are all zero
            proportions = needed_df.loc[idx].clip(lower=0) / total_needed_value
        else:
            proportions = pd.Series([0.0] * len(branches), index=branches)
            proportions[needing_mask] = total_scores[needing_mask] / total_scores_sum
        
        # Allocate surplus based on proportions
        # استخدام floor لتقريب التوزيع النسبي للأسفل
        allocated = (proportions * total_surplus_value).apply(lambda x: math.floor(x))
        # إضافة جميع الفروع حتى لو كانت القيمة 0 لضمان استخدام proportional allocation
        allocated_dict = {
            branch: int(amount)
            for branch, amount in allocated.items()
        }
        
        # إعادة توزيع الوحدات لضمان توزيع الفائض على أكبر عدد من الفروع
        needed_dict = needed_df.loc[idx].to_dict()
        
        # الفروع التي حصلت على أكثر من 1
        branches_with_more_than_one = [
            branch for branch, amount in allocated_dict.items() 
            if amount > 1 and needed_dict.get(branch, 0) > 0
        ]
        
        # الفروع التي حصلت على 0 ولكن تحتاج (مرتبة حسب avg_sales و balance)
        branches_with_zero = [
            branch for branch, amount in allocated_dict.items() 
            if amount == 0 and needed_dict.get(branch, 0) > 0
        ]
        
        # ترتيب الفروع التي لديها 0 حسب avg_sales (تنازلي) ثم balance (تصاعدي)
        if branches_with_zero:
            branch_scores = []
            for branch in branches_with_zero:
                avg_sales = branch_data[branch].iloc[idx]['avg_sales']
                balance = branch_data[branch].iloc[idx]['balance']
                branch_scores.append((branch, avg_sales, balance))
            branch_scores.sort(key=lambda x: (-x[1], x[2]))
            branches_with_zero = [b[0] for b in branch_scores]
        
        # إعادة التوزيع: خصم 1 من الفروع التي لديها > 1 وإضافتها للفروع التي لديها 0
        for branch_with_more in branches_with_more_than_one:
            if not branches_with_zero:
                break
            # خصم 1 من الفرع الذي لديه أكثر من 1
            allocated_dict[branch_with_more] -= 1
            # إضافة 1 للفرع الأول الذي لديه 0 (حسب الأولوية)
            branch_to_add = branches_with_zero.pop(0)
            allocated_dict[branch_to_add] = 1
        
        allocations[idx] = allocated_dict
    
    return allocations

