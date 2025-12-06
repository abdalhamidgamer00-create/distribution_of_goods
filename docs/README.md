# Documentation Index

## 📁 Directory Structure

```
docs/
├── algorithm/          # خوارزمية التوزيع
├── verification/       # تقارير التحقق
├── tracking/           # تتبع المنتجات
├── status/             # حالة النظام
├── restructure/        # إعادة الهيكلة
└── cli_structure.md    # بنية CLI
```

---

## 📚 Algorithm Documentation

### [`algorithm/ALGORITHM_EXPLANATION.md`](algorithm/ALGORITHM_EXPLANATION.md)
شرح شامل لخوارزمية التوزيع:
- ترتيب الفروع (weighted scoring)
- التوزيع النسبي (balance=60%, need=30%, avg_sales=10%)
- الجولة الثانية لإعادة التوزيع
- أمثلة عملية (PANTOLOC, PANADOL)

### [`algorithm/ALGORITHM_UPDATES_SUMMARY.md`](algorithm/ALGORITHM_UPDATES_SUMMARY.md)
ملخص جميع التحديثات والتحسينات:
- قبل وبعد المقارنات
- الأوزان المستخدمة
- نتائج الاختبار
- الملفات المُعدلة

---

## ✅ Verification Reports

### [`verification/PANADOL_VERIFICATION_REPORT.md`](verification/PANADOL_VERIFICATION_REPORT.md)
تقرير تحقق شامل من PANADOL ADVANCE 48 TABS:
- البيانات الأولية
- تحليل تفصيلي لكل فرع
- التحويلات (جولة 1 + جولة 2)
- إجمالي الكفاءة: 89.7%

---

## 🔍 Product Tracking

### [`tracking/PANTOLOC_tracking_report.md`](tracking/PANTOLOC_tracking_report.md)
تتبع PANTOLOC 20MG 14TAB:
- 5 فروع تحتاج
- الفائض محدود
- توزيع عادل

### [`tracking/ADWIFLAM_tracking_report.md`](tracking/ADWIFLAM_tracking_report.md)
تتبع ADWIFLAM GEL 50 GM

### [`tracking/ANOXICAM_tracking_report.md`](tracking/ANOXICAM_tracking_report.md)
تتبع ANOXICAM (if exists)

---

## 📊 Status & Updates

### [`status/STATUS_UPDATE.md`](status/STATUS_UPDATE.md)
حالة النظام الحالية:
- آخر التحديثات
- الملفات المُحدثة
- الخلاصة النهائية

---

## 🏗️ Architecture & Restructure

### [`cli_structure.md`](cli_structure.md)
بنية واجهة سطر الأوامر (CLI)

### [`restructure/`](restructure/)
- `analysis.md` - تحليل إعادة الهيكلة
- `architecture.md` - معمارية النظام

---

## Quick Links

| الموضوع | الملف |
|---------|------|
| شرح الخوارزمية | [algorithm/ALGORITHM_EXPLANATION.md](algorithm/ALGORITHM_EXPLANATION.md) |
| ملخص التحديثات | [algorithm/ALGORITHM_UPDATES_SUMMARY.md](algorithm/ALGORITHM_UPDATES_SUMMARY.md) |
| التحقق من PANADOL | [verification/PANADOL_VERIFICATION_REPORT.md](verification/PANADOL_VERIFICATION_REPORT.md) |
| الحالة الحالية | [status/STATUS_UPDATE.md](status/STATUS_UPDATE.md) |
| تتبع المنتجات | [tracking/](tracking/) |
