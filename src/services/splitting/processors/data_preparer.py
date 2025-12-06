"""Data preparation for branch splitting"""

import pandas as pd
from src.core.domain.branches.config import get_base_columns, get_branches
from src.core.domain.calculations.quantity_calculator import calculate_basic_quantities
from src.core.validation.data_validator import extract_dates_from_header
from src.shared.utils.logging_utils import get_logger

logger = get_logger(__name__)


def prepare_branch_data(csv_path: str, start_date=None, end_date=None, require_dates=False) -> tuple:
    """
    Prepare branch data from CSV file
    
    Args:
        csv_path: Input CSV file path
        start_date: Optional start date (datetime), if not provided will try to extract from header
        end_date: Optional end date (datetime), if not provided will try to extract from header
        require_dates: If True, will raise error if no dates found; if False, will use default 90 days
        
    Returns:
        Tuple of (branch_data dict, has_date_header bool, first_line str)
        
    Raises:
        FileNotFoundError: If file doesn't exist
        ValueError: If required columns are missing or (if require_dates=True) no date information available
    """
    # قراءة السطر الأول
    with open(csv_path, 'r', encoding='utf-8-sig') as f:
        first_line = f.readline().strip()
    
    # محاولة الحصول على التواريخ
    # 1. استخدام التواريخ المُمررة (إن وجدت)
    # 2. استخراج من header (إن وجد)
    extracted_start, extracted_end = extract_dates_from_header(first_line)
    header_contained_dates = bool(extracted_start and extracted_end)

    if start_date is None:
        start_date = extracted_start
    if end_date is None:
        end_date = extracted_end
    
    has_date_info = bool(start_date and end_date)
    
    # إذا كانت التواريخ مطلوبة ولم توجد، رفع خطأ
    if require_dates and not has_date_info:
        raise ValueError(
            "❌ خطأ: لم يتم العثور على معلومات التاريخ!\n"
            "يجب توفير التواريخ إما:\n"
            "1. في السطر الأول من الملف بالصيغة: من: DD/MM/YYYY HH:MM إلى: DD/MM/YYYY HH:MM\n"
            "2. أو تمريرها كمعاملات (start_date, end_date)\n"
            "مثال: من: 01/09/2024 00:00 إلى: 03/12/2024 00:00"
        )
    
    # حساب عدد الأيام
    from src.core.validation.data_validator import calculate_days_between
    
    if has_date_info:
        num_days = calculate_days_between(start_date, end_date)
        
        if num_days <= 0:
            raise ValueError(
                f"❌ خطأ: نطاق التاريخ غير صالح!\n"
                f"تاريخ البداية: {start_date}\n"
                f"تاريخ النهاية: {end_date}\n"
                f"عدد الأيام المحسوب: {num_days}\n"
                "يجب أن يكون تاريخ النهاية بعد تاريخ البداية."
            )
        
        logger.info(f"✅ Date range: {num_days} days from {start_date} to {end_date}")
    else:
        # استخدام قيمة افتراضية (90 يوم = 3 أشهر تقريباً)
        num_days = 90
        logger.warning(f"⚠️ No date information found. Using default: {num_days} days for avg_sales calculation")
    
    # قراءة CSV
    # skiprows depends on whether the *header itself* contained date info
    if header_contained_dates:
        df = pd.read_csv(csv_path, skiprows=1, encoding='utf-8-sig')
    else:
        df = pd.read_csv(csv_path, encoding='utf-8-sig')
    
    # التحقق من وجود البيانات
    if df.empty:
        raise ValueError("CSV file contains no data")
    
    branches = get_branches()
    base_columns = get_base_columns()
    branch_data = {}
    
    # التحقق من وجود الأعمدة المطلوبة فقط (sales و balance)
    # avg_sales اختيارية وسيتم حسابها
    required_columns = set(base_columns)
    for branch in branches:
        required_columns.update([
            f'{branch}_sales',
            f'{branch}_balance'
        ])
    
    missing_columns = required_columns - set(df.columns)
    if missing_columns:
        raise ValueError(f"Missing required columns: {missing_columns}")
    
    # تحضير البيانات لكل فرع
    for branch in branches:
        # الأعمدة الإلزامية
        required_branch_cols = [
            f'{branch}_sales',
            f'{branch}_balance'
        ]
        
        # اختيار الأعمدة
        selected_columns = base_columns + required_branch_cols
        branch_df = df[selected_columns].copy()
        
        # إعادة تسمية الأعمدة
        branch_df.columns = base_columns + ['sales', 'balance']
        
        # حساب avg_sales دائماً من sales وعدد الأيام
        # تجاهل أي قيمة avg_sales مرسلة من المستخدم لتجنب الأخطاء
        branch_df['avg_sales'] = branch_df['sales'] / num_days
        logger.info(f"✅ Calculated avg_sales for {branch}: sales / {num_days} days")
        
        branch_df = calculate_basic_quantities(branch_df)
        branch_data[branch] = branch_df
    
    logger.info("Prepared data for %d branches, %d products", 
                len(branches), len(branch_data[branches[0]]))
    
    return branch_data, header_contained_dates, first_line

