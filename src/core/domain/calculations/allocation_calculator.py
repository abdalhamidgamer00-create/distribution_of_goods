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
    
    allocations = {}
    for idx in total_needed[needs_mask].index:
        denom = total_needed.loc[idx]
        if denom <= 0:
            continue
        total_surplus_value = total_surplus.loc[idx]
        proportions = needed_df.loc[idx].clip(lower=0) / denom
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

