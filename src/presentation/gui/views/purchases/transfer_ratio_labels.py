"""Labels and constants for the transfer ratio page."""

PAGE_TITLE = "نسبة التحويل"
PAGE_ICON = "📊"
PAGE_DESCRIPTION = (
    "قارن بين ملف التحويل المتوقع وملف التحويل النهائي لمعرفة نسبة "
    "الأصناف التي تم تحويلها فعليًا."
)
PAGE_INFO = (
    "ارفع ملفًا واحدًا أو عدة ملفات Excel في كل جانب: ملفات التحويلات "
    "المتوقعة بين الفروع، ثم ملفات التحضير النهائي. سيتم دمج كل "
    "الملفات المرفوعة في كل جانب ثم حساب نسبة التحويل النهائية."
)
CODE_ONLY_INFO = (
    "هذا الملف النهائي لا يحتوي على بيانات الفروع، لذلك تم احتساب "
    "النسبة على مستوى الأصناف فقط."
)
RESULT_KEY = "transfer_ratio_result"

BRANCH_SUMMARY_LABELS = {
    "source_branch": "الفرع",
    "expected_items": "الأصناف المتوقعة",
    "matched_items": "الأصناف المطابقة",
    "missing_items": "الأصناف الناقصة",
    "item_ratio": "نسبة التحويل %",
    "expected_quantity": "الكمية المتوقعة",
    "matched_quantity": "الكمية المطابقة",
    "quantity_ratio": "نسبة الكميات %",
}

MISSING_LABELS = {
    "source_branch": "الفرع المصدر",
    "target_branch": "الفرع المستهدف",
    "code": "الكود",
    "product_name": "اسم الصنف",
    "quantity": "الكمية المتوقعة",
}

UNEXPECTED_LABELS = {
    "source_branch": "الفرع المصدر",
    "target_branch": "الفرع المستهدف",
    "code": "الكود",
    "product_name": "اسم الصنف",
    "quantity": "الكمية النهائية",
}
