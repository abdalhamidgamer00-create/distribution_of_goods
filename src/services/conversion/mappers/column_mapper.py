"""Column name mapping from Arabic to English"""


def get_column_mapping() -> dict:
    """
    Get mapping dictionary from Arabic column names to English
    
    Returns:
        Dictionary mapping Arabic column names to English
    """
    return {
        "كود": "code",
        "إسم الصنف": "product_name",
        "سعر البيع": "selling_price",
        "الشركة": "company",
        "الوحدة": "unit",
        "مبيعات الادارة": "admin_sales",
        "متوسط مبيعات الادارة": "admin_avg_sales",
        "رصيد الادارة": "admin_balance",
        "مبيعات الشهيد": "shahid_sales",
        "متوسط مبيعات الشهيد": "shahid_avg_sales",
        "رصيد الشهيد": "shahid_balance",
        "مبيعات العشرين": "asherin_sales",
        "متوسط مبيعات العشرين": "asherin_avg_sales",
        "رصيد العشرين": "asherin_balance",
        "مبيعات العقبى": "akba_sales",
        "متوسط مبيعات العقبى": "akba_avg_sales",
        "رصيد العقبى": "akba_balance",
        "مبيعات النجوم": "nujum_sales",
        "متوسط مبيعات النجوم": "nujum_avg_sales",
        "رصيد النجوم": "nujum_balance",
        "مبيعات الوردانى": "wardani_sales",
        "متوسط مبيعات الوردانى": "wardani_avg_sales",
        "رصيد الوردانى": "wardani_balance",
        "إجمالى المبيعات": "total_sales",
        "إجمالى رصيد الصنف": "total_product_balance"
    }

