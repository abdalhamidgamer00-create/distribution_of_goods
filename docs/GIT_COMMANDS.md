# أوامر Git للرفع على GitHub

## 1. التحضير الأول (مرة واحدة فقط)

### إنشاء مستودع على GitHub:
1. اذهب إلى https://github.com
2. اضغط "New repository"
3. أدخل اسم المشروع: `distribution_of_goods`
4. اضغط "Create repository"

### ربط المشروع المحلي بـ GitHub:

```bash
cd /home/abdo/Public/python_project/distribution_of_goods

# 1. تهيئة Git (إذا لم يكن مهيأ)
git init

# 2. إضافة remote (استبدل YOUR_USERNAME باسم المستخدم)
git remote add origin https://github.com/YOUR_USERNAME/distribution_of_goods.git

# 3. التحقق من الـ remote
git remote -v
```

---

## 2. الرفع على GitHub (كل مرة)

### الخطوات الأساسية:

```bash
# 1. إضافة جميع الملفات المتغيرة
git add .

# 2. عمل commit مع رسالة وصفية
git commit -m "وصف التغييرات"

# 3. رفع على GitHub
git push -u origin main
```

### أول مرة فقط:

```bash
# إذا كانت أول مرة، قد تحتاج:
git branch -M main
git push -u origin main
```

---

## 3. أمثلة لرسائل Commit جيدة

```bash
git commit -m "Fix TypeError in balance column conversion"
git commit -m "Update algorithm to use balance limit of 30"
git commit -m "Add second round redistribution logic"
git commit -m "Update documentation for algorithm changes"
```

---

## 4. قبل الرفع: إضافة .gitignore

قبل رفع الكود، أنشئ ملف `.gitignore` لتجنب رفع ملفات غير ضرورية:

```bash
# إنشاء .gitignore
cat > .gitignore << 'EOF'
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
.venv/
venv/
env/

# Data files (لا نرفع البيانات)
data/input/
data/output/
data/logs/
data/archive/

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

# Temporary files
*.tmp
*.log
EOF

git add .gitignore
git commit -m "Add .gitignore file"
```

---

## 5. الأوامر الكاملة (نسخ ولصق)

### للمرة الأولى:

```bash
cd /home/abdo/Public/python_project/distribution_of_goods

# تهيئة
git init
git branch -M main

# إضافة remote (استبدل YOUR_USERNAME)
git remote add origin https://github.com/YOUR_USERNAME/distribution_of_goods.git

# إضافة .gitignore
cat > .gitignore << 'EOF'
__pycache__/
*.py[cod]
.Python
.venv/
venv/
data/input/
data/output/
data/logs/
data/archive/
.vscode/
.idea/
.DS_Store
*.log
EOF

# أول commit
git add .
git commit -m "Initial commit: Distribution of Goods system"
git push -u origin main
```

### للمرات التالية:

```bash
cd /home/abdo/Public/python_project/distribution_of_goods

# إضافة التغييرات
git add .

# Commit
git commit -m "وصف التغييرات"

# رفع
git push
```

---

## 6. أوامر مفيدة

```bash
# معرفة حالة الملفات
git status

# معرفة التغييرات
git diff

# تاريخ الـ commits
git log --oneline

# التراجع عن تغييرات قبل commit
git restore <file>

# التراجع عن آخر commit (بدون حذف التغييرات)
git reset --soft HEAD~1
```

---

## 7. إذا كان المستودع موجود مسبقاً

```bash
# استنساخ من GitHub
git clone https://github.com/YOUR_USERNAME/distribution_of_goods.git

# الدخول للمجلد
cd distribution_of_goods

# بعد التعديلات
git add .
git commit -m "وصف"
git push
```

---

## ملاحظات مهمة

1. **لا ترفع البيانات الحساسة**: ملفات Excel/CSV الأصلية
2. **استخدم .gitignore**: لاستبعاد الملفات غير المطلوبة
3. **رسائل Commit واضحة**: صف ماذا غيرت بدقة
4. **Commit صغيرة متكررة**: أفضل من commit كبيرة نادرة

---

## التحقق من النجاح

بعد `git push`، اذهب إلى:
```
https://github.com/YOUR_USERNAME/distribution_of_goods
```

يجب أن ترى الكود على GitHub! ✅
