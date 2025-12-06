"""CSV branch splitter"""

import os
from time import perf_counter

from src.core.domain.branches.config import get_branches
from src.services.splitting.processors.data_preparer import prepare_branch_data
from src.core.domain.calculations.allocation_calculator import (
    calculate_proportional_allocations_vectorized,
)
from src.core.domain.calculations.order_calculator import get_needing_branches_order_for_product
from src.services.splitting.processors.surplus_finder import (
    find_surplus_sources_for_single_product,
)
from src.core.domain.calculations.quantity_calculator import calculate_surplus_remaining
from src.services.splitting.processors.withdrawal_processor import process_withdrawals
from src.services.splitting.writers.file_writer import write_branch_files, write_analytics_files
from src.shared.utils.logging_utils import get_logger

logger = get_logger(__name__)


def split_csv_by_branches(csv_path: str, output_base_dir: str, base_filename: str, analytics_dir: str = None) -> tuple:
    """
    Split CSV file by branches into separate files
    
    Args:
        csv_path: Input CSV file path
        output_base_dir: Base directory for output files
        base_filename: Base filename (without extension)
        analytics_dir: Directory for analytics files (optional)
        
    Returns:
        Tuple of (dict of branch output files, timing stats dict)
        
    Raises:
        FileNotFoundError: If CSV file doesn't exist
        ValueError: If CSV file is empty or invalid
    """
    # التحقق من وجود الملف
    if not os.path.exists(csv_path):
        raise FileNotFoundError(f"CSV file not found: {csv_path}")
    
    # التحقق من حجم الملف
    if os.path.getsize(csv_path) == 0:
        raise ValueError(f"CSV file is empty: {csv_path}")
    
    timing_stats = {}
    branches = get_branches()
    
    try:
        # 1. تحضير البيانات
        prep_start = perf_counter()
        branch_data, has_date_header, first_line = prepare_branch_data(csv_path)
        timing_stats["prep_time"] = perf_counter() - prep_start
        
        # التحقق من وجود البيانات
        if not branch_data or branches[0] not in branch_data:
            raise ValueError("No data found in CSV file")
        
        num_products = len(branch_data[branches[0]])
        timing_stats["num_products"] = num_products
        
        if num_products == 0:
            raise ValueError("CSV file contains no products")
        
        # 2. حساب التوزيع النسبي
        allocation_start = perf_counter()
        proportional_allocation = calculate_proportional_allocations_vectorized(branch_data, branches)
        timing_stats["allocation_time"] = perf_counter() - allocation_start
        
        # 3. البحث عن الفائض
        surplus_start = perf_counter()
        all_withdrawals = {}
        analytics_data = {}
        max_withdrawals = 0
        
        # تهيئة analytics_data لكل فرع
        for branch in branches:
            branch_df = branch_data[branch].copy()
            # إنشاء قائمة فارغة لكل منتج
            withdrawals_list = []
            analytics_data[branch] = (branch_df, withdrawals_list)
        
        # معالجة كل منتج على حدة بترتيب فروع خاص به
        num_products = len(branch_data[branches[0]])
        
        for product_idx in range(num_products):
            # الحصول على ترتيب الفروع التي تحتاج هذا المنتج
            needing_branches = get_needing_branches_order_for_product(
                product_idx, branch_data, branches
            )
            
            # معالجة كل فرع في الترتيب المحدد لهذا المنتج فقط
            for branch in needing_branches:
                branch_df = analytics_data[branch][0]
                needed = branch_df.iloc[product_idx]['needed_quantity']
                
                if needed > 0:
                    # معالجة هذا المنتج فقط لهذا الفرع
                    withdrawals_list, withdrawals = find_surplus_sources_for_single_product(
                        branch, product_idx, branch_data, branches,
                        all_withdrawals, proportional_allocation
                    )
                    
                    # تحديث السحوبات الإجمالية
                    for key, amount in withdrawals.items():
                        all_withdrawals[key] = all_withdrawals.get(key, 0.0) + amount
                    
                    # تحديث analytics_data
                    existing_withdrawals_list = analytics_data[branch][1]
                    # إضافة سجلات فارغة للمنتجات السابقة إذا لزم الأمر
                    while len(existing_withdrawals_list) < product_idx:
                        existing_withdrawals_list.append([{
                            'surplus_from_branch': 0.0,
                            'available_branch': '',
                            'surplus_remaining': 0.0,
                            'remaining_needed': 0.0
                        }])
                    existing_withdrawals_list.append(withdrawals_list)
                    
                    # حساب العدد الأقصى للسحوبات
                    max_withdrawals = max(max_withdrawals, len(withdrawals_list))
        
        # معالجة المنتجات التي لا تحتاجها أي فرع (إضافة سجلات فارغة)
        for branch in branches:
            branch_df = analytics_data[branch][0]
            existing_withdrawals_list = analytics_data[branch][1]
            
            # إضافة سجلات فارغة للمنتجات المتبقية
            for product_idx in range(len(existing_withdrawals_list), num_products):
                needed = branch_df.iloc[product_idx]['needed_quantity']
                if needed <= 0:
                    existing_withdrawals_list.append([{
                        'surplus_from_branch': 0.0,
                        'available_branch': '',
                        'surplus_remaining': 0.0,
                        'remaining_needed': 0.0
                    }])
        
        timing_stats["surplus_time"] = perf_counter() - surplus_start
        
        # SECOND ROUND: إعادة توزيع الفائض المهدر من قاعدة balance>=15
        from src.services.splitting.processors.surplus_redistributor import redistribute_wasted_surplus
        
        max_withdrawals, second_round_time = redistribute_wasted_surplus(
            branches=branches,
            branch_data=branch_data,
            analytics_data=analytics_data,
            all_withdrawals=all_withdrawals,
            max_withdrawals=max_withdrawals,
            num_products=num_products,
            balance_limit=15.0
        )
        timing_stats["second_round_time"] = second_round_time
        
        # 4. حساب الفائض المتبقي
        final_surplus_remaining_dict = calculate_surplus_remaining(
            branches, branch_data, all_withdrawals
        )
        
        # 5. معالجة السحوبات
        processed_data = process_withdrawals(
            branches, analytics_data, max_withdrawals, final_surplus_remaining_dict
        )
        
        # 6. كتابة الملفات
        write_start = perf_counter()
        output_files = write_branch_files(
            branches, processed_data, output_base_dir, 
            base_filename, has_date_header, first_line
        )
        
        if analytics_dir is None:
            analytics_dir = os.path.normpath(
                os.path.join(output_base_dir, "..", "analytics")
            )
        
        write_analytics_files(
            branches, processed_data, analytics_dir, 
            base_filename, max_withdrawals, has_date_header, first_line
        )
        timing_stats["write_time"] = perf_counter() - write_start
        
        return output_files, timing_stats
        
    except FileNotFoundError:
        raise
    except ValueError:
        raise
    except Exception as e:
        logger.exception("Error splitting CSV: %s", e)
        raise ValueError(f"Error splitting CSV: {e}") from e
