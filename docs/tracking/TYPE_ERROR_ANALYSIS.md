# تحليل الخطأ: TypeError - السبب الحقيقي

## المشكلة المكتشفة! 🔍

### البيانات في الملف:
```csv
code,product_name,...,admin_balance,shahid_balance,...
71475,+*** IMP BIOTIN,...,0,0,...  ← integer!
ANAF,+***IMP ANAFRANIL,...,0,0,...  ← integer!
76161,+***IMP DEVIT-3,...,7,1,...  ← integer!
```

**المشكلة**: عمود `balance` يحتوي على **integers** (0, 1, 7) بدلاً من **floats** (0.0, 1.0, 7.0)!

---

## لماذا يسبب هذا خطأ؟

### عند القراءة:
```python
# pandas يقرأ العمود
df = pd.read_csv(...)

# إذا كل القيم integers → pandas يعتبره int64
balance = [0, 0, 7, 1, ...]  # int64

# لكن monthly_quantity (من avg_sales * 30) → float64
monthly_quantity = [0.0, 0.0, 2.7, ...]  # float64

# عند الطرح
balance - monthly_quantity  # int64 - float64
# → في بعض الحالات يعمل، لكن إذا فيه قيم mixed...
```

### لكن الخطأ يقول `str - int`!

دعني أعيد الفحص...

---

## إعادة التحليل ✅

من الخطأ:
```
TypeError: unsupported operand type(s) for -: 'str' and 'int'
```

السبب **الحقيقي**:
1. في **بعض الصفوف** من الـCSV، `balance` يحتوي على **نص** (مثل `-` أو `N/A` أو فراغ)
2. pandas **يقرأ العمود كـ object** (string) بدلاً من numeric
3. عند الطرح: `'text' - int` → **Error!**

---

## الحل النهائي

### في `data_preparer.py` السطر ~113:

```python
# ❌ قبل (بدون تحويل)
branch_df = df[selected_columns].copy()
branch_df.columns = base_columns + ['sales', 'balance']
branch_df['avg_sales'] = branch_df['sales'] / num_days

# ✅ بعد (مع تحويل صريح)
branch_df = df[selected_columns].copy()
branch_df.columns = base_columns + ['sales', 'balance']

# Convert to numeric, coerce errors to NaN, fill with 0
branch_df['sales'] = pd.to_numeric(branch_df['sales'], errors='coerce').fillna(0.0)
branch_df['balance'] = pd.to_numeric(branch_df['balance'], errors='coerce').fillna(0.0)

branch_df['avg_sales'] = branch_df['sales'] / num_days
```

**الفوائد**:
- `pd.to_numeric()`: يحول أي شيء لرقم
- `errors='coerce'`: القيم غير صالحة (نصوص) → NaN
- `.fillna(0.0)`: NaN → 0.0
- **يضمن**: balance و sales دائماً float64

---

## ملخص

| العنصر | التفاصيل |
|--------|-----------|
| **الخطأ** | `str - int` في `balance - monthly_quantity` |
| **السبب** | `balance` يحتوي على نصوص في بعض الصفوف |
| **الملف المشكل** | `selled_stocknew_renamed_20251210_010152.csv` |
| **السبب الخفي** | قيم غير رقمية (نص أو فراغ) في عمود balance |
| **الحل** | `pd.to_numeric(errors='coerce').fillna(0)` |

**جاهز للتطبيق!** ✅
