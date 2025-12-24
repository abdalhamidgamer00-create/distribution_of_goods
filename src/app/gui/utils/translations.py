"""GUI translations and string constants."""

STEP_NAMES = {
    "1": "أرشفة البيانات", "2": "استيراد البيانات",
    "3": "التحقق من البيانات", "4": "تحليل المبيعات",
    "5": "توحيد العناوين", "6": "توزيع الفروع",
    "7": "تحسين التحويلات", "8": "تصنيف المنتجات",
    "9": "تقرير الفائض", "10": "تقرير النقص",
    "11": "الدمج النهائي"
}

STEP_DESCRIPTIONS = {
    "1": "أرشفة ومسح بيانات المخرجات السابقة لبدء دورة جديدة",
    "2": "تحويل ملف Excel محدد من مجلد الإدخال إلى CSV",
    "3": "التحقق من بيانات CSV بنطاق التاريخ ورؤوس الأعمدة",
    "4": "إنشاء تقرير تحليل مبيعات شامل مع إحصائيات",
    "5": "إعادة تسمية أعمدة CSV من العربية إلى الإنجليزية",
    "6": "تقسيم ملف CSV إلى 6 ملفات منفصلة لكل فرع",
    "7": "إنشاء ملفات CSV للتحويل بين الفروع",
    "8": "تصنيف ملفات التحويل إلى 6 فئات وإلى Excel",
    "9": "إنشاء ملفات للمنتجات ذات الفائض المتبقي",
    "10": "إنشاء ملفات للمنتجات التي يتجاوز فيها الاحتياج",
    "11": "دمج التحويلات مع الفائض في ملفات مجمعة/منفصلة"
}

CATEGORY_NAMES = {
    "tablets_and_capsules": "أقراص وكبسولات",
    "injections": "حقن",
    "syrups": "شراب",
    "creams": "كريمات ومرطبات",
    "sachets": "أكياس",
    "other": "أخرى"
}

BRANCH_NAMES = {
    "administration": "الادارة",
    "asherin": "العشرين",
    "star": "النجوم",
    "shahid": "الشهيد",
    "okba": "العقبى",
    "wardani": "الوردانى"
}

MESSAGES = {
    "success": "تم بنجاح", 
    "failed": "فشل",
    "error": "حدث خطأ", 
    "warning": "تحذير",
    "info": "معلومة", 
    "running": "جاري التنفيذ...", 
    "completed": "اكتمل",
    "no_files": "لا توجد ملفات", 
    "select_file": "اختر ملف",
    "download": "تحميل", 
    "download_all": "تحميل الكل", 
    "view": "عرض",
    "transfers": "ملفات التحويل", 
    "remaining_surplus": "الفائض المتبقي",
    "file_not_found": "الملف غير موجود", 
    "no_data": "لا توجد بيانات للعرض",
    "prerequisite_missing": "المتطلب '{prerequisite}' غير جاهز",
    "contract_violation": "مخالفة في عقد الخدمة '{service}'"
}

COLUMNS = {
    "code": "كود",
    "product_name": "إسم الصنف",
    "total_sales": "إجمالي المبيعات", 
    "shortage_quantity": "كمية النقص",
    "needed_quantity": "الكمية المطلوبة",
    "surplus_quantity": "كمية الفائض",
    "sender_balance": "رصيد الراسل",
    "receiver_balance": "رصيد المستلم",
    "target_branch": "الفرع المستهدف"
}

REPORT_HEADERS = {
    "code": "كود",
    "product_name": "إسم الصنف",
    "total_sales": "إجمالي المبيعات", 
    "shortage_quantity": "كمية النقص",
    "needed_quantity": "الكمية المطلوبة",
    "surplus_quantity": "كمية الفائض",
    "sender_balance": "رصيد الراسل",
    "receiver_balance": "رصيد المستلم",
    "target_branch": "الفرع المستهدف"
}
