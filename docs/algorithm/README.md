# فهرس مجلد الخوارزمية (Algorithm Documentation)

## الملفات

### 1. [ALGORITHM_EXPLANATION.md](ALGORITHM_EXPLANATION.md)
**الشرح الشامل للخوارزمية - الإصدار المُحدث**

يحتوي على:
- الثوابت الأساسية (MAX_ALLOWED_BALANCE = 30)
- المراحل الأربع الرئيسية
- حساب الكميات والنقاط الموزونة
- منطق الجولتين (الأولى والثانية)
- القواعد الأساسية والضمانات
- أمثلة عملية (ACYCLOVIR, PANADOL)
- جميع التحديثات الأخيرة

**آخر تحديث**: 6 ديسمبر 2025

---

### 2. [ALGORITHM_UPDATES_SUMMARY.md](ALGORITHM_UPDATES_SUMMARY.md)
**ملخص التحديثات الرئيسية**

يحتوي على:
- تغيير حد الرصيد الأقصى (15 → 30)
- تحديث منطق الجولة الثانية
- تغيير ترتيب الأولوية
- أمثلة قبل وبعد
- الفوائد والملاحظات
- الملفات المتأثرة

**آخر تحديث**: 6 ديسمبر 2025

---

## التحديثات الرئيسية (نظرة سريعة)

### ✅ ديسمبر 2025:

1. **حد الرصيد الأقصى**: 15 → **30**
2. **هدف الجولة الثانية**: الوصول لـ15 → **تغطية remaining_needed فقط**
3. **قيد عدم التجاوز**: ضمني → **صريح (min)**
4. **ترتيب الأولوية**: avg_sales أولاً → **balance أولاً**

---

## الملفات المرتبطة

### الكود الرئيسي:
- `src/services/splitting/processors/target_calculator.py`
- `src/services/splitting/processors/surplus_redistributor.py`
- `src/services/splitting/processors/surplus_finder.py`
- `src/core/domain/calculations/allocation_calculator.py`

### التوثيق الإضافي:
- `docs/tracking/SECOND_ROUND_FINAL_LOGIC.md`
- `docs/tracking/BALANCE_LIMIT_CHANGE.md`
- `docs/tracking/SECOND_ROUND_SORT_ORDER.md`

---

## بدء سريع

### لفهم الخوارزمية:
1. اقرأ [ALGORITHM_EXPLANATION.md](ALGORITHM_EXPLANATION.md) - الشرح الكامل
2. اطلع على الأمثلة العملية في نهاية الملف

### لمعرفة التحديثات:
1. اقرأ [ALGORITHM_UPDATES_SUMMARY.md](ALGORITHM_UPDATES_SUMMARY.md)
2. راجع الأمثلة قبل/بعد

### للتطبيق العملي:
1. راجع ملفات tracking للمنتجات المحددة:
   - `docs/tracking/acyclovir/`
   - `docs/tracking/panadol/`

---

**ملاحظة**: هذا المجلد يحتوي على **الشرح النظري** للخوارزمية. للتحليلات العملية، راجع `docs/tracking/`.

**الإصدار**: 2.0  
**آخر تحديث**: 6 ديسمبر 2025
