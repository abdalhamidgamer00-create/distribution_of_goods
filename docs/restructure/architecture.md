# البنية المقترحة بعد إعادة التنظيم

## مستويات المشروع
1. **app/**
   - `app/cli`: واجهة CLI والقوائم والتعامل مع المُدخلات من المستخدم.
   - `app/pipeline`: تنفيذ الخطوات 1-9 وتدفق المعالجة (handers + orchestration).

2. **core/**
   - `core/domain`: كائنات الدومين (التحليل، التصنيف، الحسابات) وتشمل:
     - analyzers
     - classifiers
     - calculations (الملفات الحالية في calculators)
   - `core/validation`: التحقق من البيانات (validators + قواعد الأعمدة).

3. **services/**
   - `services/conversion`: التحويل بين Excel/CSV وإعادة تسمية الأعمدة.
   - `services/splitting`: منطق تقسيم الفروع (processors/writers الحاليين بعد تفكيكهم).
   - `services/transfers`: توليد ملفات التحويل وتقسيمها حسب النوع/الصيغة.

4. **shared/**
   - `shared/utils`: أدوات النظام (file handler، logging، archiver).
   - `shared/dataframes`: وظائف مشتركة للتعامل مع DataFrame (التحقق من الأعمدة، تنظيف البيانات).
   - `shared/reporting`: التقارير والمخرجات النصية.

## خطة نقل الملفات
| الموقع الحالي | الموقع الجديد | ملاحظات |
|---------------|---------------|---------|
| `src/cli` | `src/app/cli` | تحديث المسارات في main.py |
| `src/config` | `src/app/pipeline` | إعادة تسمية step handlers إلى `step_X.py` داخل pipeline |
| `src/analyzers`, `src/classifiers` | `src/core/domain/{analysis,classification}` | تبسيط الأسماء ووضع __init__ جديد |
| `src/splitters/calculators` | `src/core/domain/calculations` | دمج مع الحسابات الأخرى |
| `src/splitters/processors`, `splitters/writers` | `src/services/splitting/{processors,writers}` | | 
| `src/transfer_generators` | `src/services/transfers` | توحيد المولدات والمقسّمات |
| `src/converters`, `src/mappers` | `src/services/conversion` و `src/shared/dataframes` | نقل وظائف التحويل |
| `src/utils` | `src/shared/utils` | مع فصل وظائف DataFrame إلى وحدة جديدة |
| `src/reporters` | `src/shared/reporting` | |

## إزالة التكرار
- إنشاء وحدة جديدة `shared/dataframes/validators.py` تحتوي على:
  - `ensure_columns(df, required_columns, context)`
  - `safe_numeric(value)`
- استبدال المنطق المكرر في `transfer_generator` و `transfer_generators/splitters/file_splitter.py` بهذه الدوال.

## تحسين قابلية الاختبار
- إنشاء سكربت `tests/run_pipeline_smoke.py` لتشغيل الخطوات 1-9 على نسخة مصغرة من البيانات (subsample من CSV).
- إضافة واجهة `app/pipeline/runner.py` تسمح بتشغيل الخطوات برمجياً بدلاً من الاعتماد على المدخلات اليدوية فقط.

## التحقق النهائي
- بعد الترحيل، يتم تحديث `main.py` لاستدعاء البنية الجديدة.
- تحديث `requirements.txt` إذا لزم الأمر (لا تغييرات حالياً).
