# ترتيب الفروع عند تساوي الفائض

## السؤال
**عند تساوي surplus_quantity بين فرعين أو أكثر، كيف يتم الترتيب؟**

---

## الإجابة

### الكود الحالي:
**الملف**: `src/core/domain/calculations/order_calculator.py`

```python
def get_surplus_branches_order_for_product(idx, branch, branch_data, branches, existing_withdrawals):
    """
    ترتيب الفروع حسب الفائض المتاح.
    
    الترتيب:
    1. available_surplus (تنازلي - الأكبر أولاً)
    """
    
    surplus_branches = []
    
    for other_branch in branches:
        if other_branch == branch:  # تخطي الفرع نفسه
            continue
        
        # حساب الفائض المتاح
        available_surplus = calculate_available_surplus(...)
        
        if available_surplus > 0:
            surplus_branches.append((other_branch, available_surplus))
    
    # الترتيب: حسب available_surplus فقط (تنازلي)
    surplus_branches.sort(key=lambda x: -x[1])
    
    return [b[0] for b in surplus_branches]
```

---

## التحليل

### الترتيب الحالي:
```python
sort(key=lambda x: -x[1])  # x[1] = available_surplus
```

**المشكلة**: عند التساوي، **الترتيب عشوائي** (حسب الترتيب الأصلي في القائمة)!

---

## الحل المقترح

### الخيار 1: الترتيب حسب avg_sales (الأعلى نشاطاً يعطي أولاً)

```python
# ترتيب: surplus (تنازلي) ثم avg_sales (تنازلي)
surplus_branches = []

for other_branch in branches:
    if other_branch == branch:
        continue
    
    available_surplus = calculate_available_surplus(...)
    
    if available_surplus > 0:
        avg_sales = branch_data[other_branch].iloc[idx]['avg_sales']
        surplus_branches.append((other_branch, available_surplus, avg_sales))

# الترتيب: surplus أولاً، avg_sales ثانياً
surplus_branches.sort(key=lambda x: (-x[1], -x[2]))
```

**المنطق**: الفروع الأكثر نشاطاً (مبيعات) تحتفظ بمخزونها أكثر.

---

### الخيار 2: الترتيب حسب balance (الأعلى رصيداً يعطي أولاً)

```python
# ترتيب: surplus (تنازلي) ثم balance (تنازلي)
surplus_branches = []

for other_branch in branches:
    if other_branch == branch:
        continue
    
    available_surplus = calculate_available_surplus(...)
    
    if available_surplus > 0:
        balance = branch_data[other_branch].iloc[idx]['balance']
        surplus_branches.append((other_branch, available_surplus, balance))

# الترتيب: surplus أولاً، balance ثانياً
surplus_branches.sort(key=lambda x: (-x[1], -x[2]))
```

**المنطق**: الفروع الأغنى (رصيد أكبر) تتحمل العطاء أكثر.

---

### الخيار 3: الترتيب حسب المسافة/الموقع (غير متوفر حالياً)

```python
# ترتيب: surplus، ثم القرب الجغرافي
# يحتاج بيانات إضافية عن المواقع
```

---

## التوصية

### ✅ الأفضل: balance أولاً

```python
def get_surplus_branches_order_for_product(idx, branch, branch_data, branches, existing_withdrawals):
    surplus_branches = []
    
    for other_branch in branches:
        if other_branch == branch:
            continue
        
        available_surplus = calculate_available_surplus(
            branch_data, other_branch, idx, existing_withdrawals
        )
        
        if available_surplus > 0:
            balance = branch_data[other_branch].iloc[idx]['balance']
            surplus_branches.append((other_branch, available_surplus, balance))
    
    # ترتيب: surplus (تنازلي) ثم balance (تنازلي)
    surplus_branches.sort(key=lambda x: (-x[1], -x[2]))
    
    return [b[0] for b in surplus_branches]
```

**السبب**:
1. **العدالة**: الفروع الأغنى تعطي أولاً
2. **الأمان**: الفروع برصيد أكبر أقل عرضة للنفاد
3. **المنطق**: "من يملك أكثر، يعطي أولاً"

---

## مثال توضيحي

### البيانات:
| الفرع | surplus | balance | avg_sales |
|-------|---------|---------|-----------|
| A | **10** | 25 | 0.5 |
| B | **10** | 20 | 0.7 |
| C | 8 | 30 | 0.3 |

### الترتيب الحالي (surplus فقط):
```
1. A أو B (عشوائي - نفس surplus=10)
2. B أو A (عشوائي)
3. C (surplus=8)
```

### الترتيب المقترح (surplus ثم balance):
```
1. A (surplus=10, balance=25) ✅
2. B (surplus=10, balance=20)
3. C (surplus=8, balance=30)
```

### الترتيب البديل (surplus ثم avg_sales):
```
1. B (surplus=10, avg_sales=0.7) ✅
2. A (surplus=10, avg_sales=0.5)
3. C (surplus=8, avg_sales=0.3)
```

---

## الخلاصة

### الوضع الحالي:
- ✅ الترتيب حسب surplus (الأكبر أولاً)
- ❌ عند التساوي: **عشوائي**

### المقترح:
- ✅ surplus (الأكبر أولاً)
- ✅ **عند التساوي**: balance (الأكبر أولاً)

**الفائدة**: 
- ضمان ترتيب ثابت ومنطقي
- الفروع الأغنى تعطي أولاً (أكثر أماناً)
- العدالة في التوزيع

---

## التطبيق

لتطبيق هذا التحسين، يجب تعديل:
**الملف**: `src/core/domain/calculations/order_calculator.py`  
**الدالة**: `get_surplus_branches_order_for_product()`

**التعديل**:
```python
# إضافة balance للترتيب
surplus_branches.append((other_branch, available_surplus, balance))
surplus_branches.sort(key=lambda x: (-x[1], -x[2]))
```

**هل تريد تطبيق هذا التحسين؟** 🤔
