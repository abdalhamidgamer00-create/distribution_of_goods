"""Constants used by transfer ratio comparison services."""

BRANCH_PATTERNS = {
    "administration": ["administration", "الادارة", "الإدارة"],
    "asherin": ["asherin", "العشرين"],
    "star": ["star", "النجوم", "نجوم"],
    "shahid": ["shahid", "الشهيد"],
    "okba": ["okba", "العقبي", "العقبى"],
    "wardani": ["wardani", "الورداني", "الوردانى"],
}

COLUMN_ALIASES = {
    "code": ["code", "كود"],
    "product_name": [
        "product_name",
        "اسم_الصنف",
        "اسم_الصنف_",
        "اسم الصنف",
        "إسم الصنف",
    ],
    "quantity": [
        "quantity_to_transfer",
        "quantity",
        "qty",
        "الكمية",
        "كمية",
        "كمية_التحويل",
        "كمية التحويل",
    ],
    "source_branch": [
        "source_branch",
        "from_branch",
        "sender_branch",
        "branch_source",
        "الفرع_المصدر",
        "الفرع المصدر",
    ],
    "target_branch": [
        "target_branch",
        "to_branch",
        "receiver_branch",
        "branch_target",
        "الفرع_المستهدف",
        "الفرع المستهدف",
    ],
}

CODE_ONLY_MODE = "code_only"
FULL_MODE = "full"
FULL_TRANSFER_KEY = "full_transfer_key"

CODE_ONLY_ASSUMPTION = (
    "هذا الملف النهائي لا يحتوي على بيانات الفروع، لذلك تمت المقارنة "
    "على مستوى الصنف `code` فقط مع استخدام الكمية لحساب نسبة الكميات."
)

FULL_ASSUMPTION = (
    "تمت المقارنة أساسًا على الصنف `code` مع استخدام الفرع المصدر "
    "والفرع المستهدف عندما يكونان متوفرين في الأعمدة أو قابلين "
    "للاستخراج من اسم الملف/اسم الشيت."
)
