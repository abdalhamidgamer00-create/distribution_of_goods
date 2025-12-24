"""Column name mapping from Arabic to English"""


def get_column_mapping() -> dict:
    """
    Get mapping dictionary from Arabic column names to English.
    Ensures zero abbreviations are used for branch IDs.
    """
    return {
        "كود": "code",
        "إسم الصنف": "product_name",
        "سعر البيع": "selling_price",
        "الشركة": "company",
        "الوحدة": "unit",
        "مبيعات الادارة": "administration_sales",
        "متوسط مبيعات الادارة": "administration_avg_sales",
        "رصيد الادارة": "administration_balance",
        "مبيعات الشهيد": "shahid_sales",
        "متوسط مبيعات الشهيد": "shahid_avg_sales",
        "رصيد الشهيد": "shahid_balance",
        "مبيعات العشرين": "asherin_sales",
        "متوسط مبيعات العشرين": "asherin_avg_sales",
        "رصيد العشرين": "asherin_balance",
        "مبيعات العقبى": "okba_sales",
        "متوسط مبيعات العقبى": "okba_avg_sales",
        "رصيد العقبى": "okba_balance",
        "مبيعات النجوم": "star_sales",
        "متوسط مبيعات النجوم": "star_avg_sales",
        "رصيد النجوم": "star_balance",
        "مبيعات الوردانى": "wardani_sales",
        "متوسط مبيعات الوردانى": "wardani_avg_sales",
        "رصيد الوردانى": "wardani_balance",
        "إجمالى المبيعات": "total_sales",
        "إجمالى رصيد الصنف": "total_product_balance"
    }
