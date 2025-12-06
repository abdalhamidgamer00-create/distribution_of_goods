# شرح الخوارزمية - الإصدار المُحدث (ديسمبر 2025)

## نظرة عامة

خوارزمية توزيع المنتجات بين الفروع، مع **تحديثات حديثة** على منطق الجولة الثانية وحد الرصيد الأقصى.

---

## الثوابت الأساسية

```python
# الحد الأقصى للرصيد (محدث من 15 إلى 30)
MAX_ALLOWED_BALANCE = 30

# أوزان التوزيع النسبي (ثابتة)
BALANCE_WEIGHT = 0.60  # 60% - أولوية للرصيد المنخفض
NEEDED_WEIGHT = 0.30   # 30% - الاحتياج
AVG_SALES_WEIGHT = 0.10  # 10% - نشاط الفرع
```

---

## المراحل الرئيسية

### المرحلة 1: حساب الكميات الأساسية

```python
# لكل منتج في كل فرع
monthly_quantity = ceil(avg_sales × 30)
surplus_quantity = max(0, floor(balance - monthly_quantity))
needed_quantity = max(0, ceil(monthly_quantity - balance))
```

**ملاحظة**: `needed` = النقص الفعلي (ليس الاحتياج الكامل)

---

### المرحلة 2: التوزيع النسبي الموزون

**متى يُطبق؟**
```python
if total_surplus < total_needed:  # نقص في الفائض
    # التوزيع النسبي بناءً على النقاط الموزونة
```

**حساب النقاط**:
```python
# 1. Normalization لكل مكون
avg_sales_norm = normalize(avg_sales_values)
needed_norm = normalize(needed_values)
balance_norm = normalize(1/balance_values)  # inverse!

# 2. النقاط الموزونة
score = (0.10 × avg_sales_norm + 
         0.30 × needed_norm + 
         0.60 × balance_norm)

# 3. التوزيع النسبي
allocated = floor(score/total_scores × total_surplus)
```

**إعادة توزيع البقايا**:
```python
remaining = total_surplus - sum(allocated)

while remaining > 0:
    # خصم 1 من فرع له > 1
    # أضف 1 لفرع له 0 (حسب الأولوية)
```

---

### المرحلة 3: الجولة الأولى للتوزيع

**الترتيب**:
```python
branches_order = sort_by_weighted_score(
    balance_weight=0.60,
    needed_weight=0.30,
    avg_sales_weight=0.10
)
```

**لكل فرع** (بالترتيب):

```python
# 1. التحقق من القيود
if balance >= 30:  # ★ محدث من 15
    skip  # لا تحويل

# 2. حساب الهدف
if balance + needed > 30:  # ★ محدث
    target = 30 - balance
else:
    target = needed

# 3. البحث عن الفائض
for supplier in suppliers_order:
    if supplier.surplus > 0:
        amount = min(target, supplier.surplus)
        transfer(supplier → branch, amount)
        target -= amount
```

---

### المرحلة 4: الجولة الثانية (★ محدثة بالكامل)

**الهدف الجديد**: تغطية `remaining_needed` فقط (ليس الوصول لـ30)

**الشروط**:
```python
# لكل فرع
if needed > 0 and current_balance < 30:  # ★ محدث من 15
    remaining_needed = needed - transferred_so_far
    
    if remaining_needed > 0:
        # ★ القيد الجديد: لا تتجاوز 30
        remaining_capacity = min(
            remaining_needed,
            30 - current_balance
        )
```

**الترتيب** (★ محدث):
```python
# 1. الأقل current_balance أولاً (الأولوية القصوى)
# 2. الأعلى avg_sales ثانياً (للتحكيم)
sort(key=lambda x: (x.current_balance, -x.avg_sales))
```

**التوزيع**:
```python
for branch in sorted_branches:
    for supplier in all_branches:
        available_surplus = supplier.surplus - already_taken
        
        if available_surplus > 0:
            transfer = min(available_surplus, remaining_capacity)
            execute_transfer(supplier → branch, transfer)
            remaining_capacity -= transfer
```

---

## القواعد الأساسية

### 1. قاعدة الحد الأقصى (★ محدثة)
```python
if balance >= 30:  # كان: >= 15
    # لا تحويل في الجولة الأولى
    skip()

if current_balance >= 30:  # كان: >= 15
    # لا تحويل في الجولة الثانية
    skip()
```

### 2. قاعدة عدم التجاوز (★ جديدة)
```python
# في الجولة الثانية
final_balance = current_balance + transfer

if final_balance > 30:  # كان: > 15
    # تقليل التحويل
    transfer = 30 - current_balance
```

### 3. قاعدة الأولوية
```python
# الجولة الأولى: حسب النقاط الموزونة
# الجولة الثانية: الأقل رصيداً أولاً (★ محدثة)
```

---

## أمثلة عملية

### مثال 1: ACYCLOVIR 10 GM CREAM

```python
# البيانات
النجوم: balance=3, needed=6, surplus=0

# الجولة الأولى
target = min(6, 30-3) = 6
received = 6 (من الورداني والإدارة)
new_balance = 3 + 6 = 9

# الجولة الثانية (★ المنطق الجديد)
remaining_needed = 6 - 6 = 0  # تم التغطية!
# → لا جولة ثانية

final_balance = 9  # ليس 15!
```

### مثال 2: PANADOL ADVANCE 48 TABS

```python
# البيانات (بعد الجولة الأولى)
العشرين: balance=4, needed=13, received=7
current_balance = 4 + 7 = 11

# الجولة الثانية
remaining_needed = 13 - 7 = 6

# ★ القيد الجديد
remaining_capacity = min(6, 30-11) = min(6, 19) = 6

# لو كان هناك فائض
# → يحصل على 6 إضافية
# → final_balance = 11 + 6 = 17
```

---

## التغييرات الرئيسية (ديسمبر 2025)

| التغيير | قبل | بعد |
|---------|-----|-----|
| **الحد الأقصى** | 15 | **30** ✅ |
| **هدف الجولة الثانية** | الوصول لـ15 | **تغطية remaining_needed** ✅ |
| **قيد عدم التجاوز** | ضمني | **صريح (min)** ✅ |
| **ترتيب الجولة الثانية** | avg_sales أولاً | **balance أولاً** ✅ |

---

## الضمانات

1. ✅ **لا تجاوز**: `final_balance <= 30` دائماً
2. ✅ **العدالة**: الأقل رصيداً له الأولوية
3. ✅ **الكفاءة**: تغطية النقص فقط (لا هدر)
4. ✅ **الشفافية**: كل خطوة موثقة ومتتبعة

---

## الملفات ذات الصلة

### الكود:
- `src/services/splitting/processors/target_calculator.py` - قواعد الحد الأقصى
- `src/services/splitting/processors/surplus_redistributor.py` - الجولة الثانية
- `src/core/domain/calculations/allocation_calculator.py` - التوزيع النسبي

### التوثيق:
- `docs/tracking/SECOND_ROUND_FINAL_LOGIC.md` - منطق الجولة الثانية
- `docs/tracking/BALANCE_LIMIT_CHANGE.md` - تغيير الحد من 15 لـ30
- `docs/tracking/SECOND_ROUND_SORT_ORDER.md` - ترتيب الأولوية

**آخر تحديث**: 6 ديسمبر 2025
