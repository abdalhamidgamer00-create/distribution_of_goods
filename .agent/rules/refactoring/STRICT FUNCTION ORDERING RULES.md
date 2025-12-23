# 🧱 STRICT FUNCTION ORDERING RULES (PYTHON)

This document defines **strict, non-negotiable rules** for how an AI model **MUST organize functions inside a single Python file**.

The purpose is **code organization only**.

❌ Do NOT change logic ❌ Do NOT refactor algorithms ❌ Do NOT optimize performance ❌ Do NOT introduce new features

---

## 🎯 SCOPE

These rules apply **ONLY** to:

- Ordering functions inside a file
- File-level readability
- Documentation placement

These rules do **NOT** cover:

- Architecture
- Business logic
- Performance
- Design patterns

---

## 🔒 HARD CONSTRAINTS (MANDATORY)

The AI model **MUST** obey all constraints below:

1. **Program behavior must remain identical**
2. **No line may exceed 80 characters**
3. **No logic changes are allowed**
4. **No new functions unless required for ordering clarity**
5. **No function deletion**
6. **No renaming unless explicitly instructed**

---

## 📄 FILE STRUCTURE (STRICT ORDER)

The file **MUST** be ordered exactly as follows, from top to bottom:

1. **Module docstring**
2. **Constants**
3. **Public functions (module API)**
4. **Private / helper functions** (prefixed with `_`)

Deviation from this order is **NOT allowed**.

---

## 📘 MODULE DOCSTRING RULES

- MUST exist
- MUST be the first element in the file
- MUST describe the module responsibility
- MUST NOT describe implementation details

---

## 🔐 PUBLIC FUNCTION RULES

A public function is any function **not** prefixed with `_`.

Rules:

- MUST appear before any private function
- MUST have a docstring
- MUST represent the main file behavior
- MUST be readable without scrolling

---

## 🔧 PRIVATE / HELPER FUNCTION RULES

A private function **MUST**:

- Be prefixed with `_`
- Appear **after** all public functions
- Never appear above a public function
- Contain no public-facing documentation

---

## 💬 COMMENTS & DOCSTRINGS

### Docstrings

- REQUIRED for:
  - Module
  - Public functions
- OPTIONAL for private functions

### Comments

- MUST explain **why**, not **what**
- MUST NOT restate obvious code behavior
- MUST be minimal

---

## 📏 LINE LENGTH RULE

- Every line **MUST** be ≤ 80 characters
- This includes:
  - Docstrings
  - Comments
  - Function definitions

If a line exceeds 80 characters, the AI **MUST rewrite formatting only**, without changing logic.

---

## 🚫 FORBIDDEN ACTIONS

The AI model **MUST NOT**:

- Change function behavior
- Merge or split logic
- Introduce abstractions
- Reorder logic inside a function
- Apply architectural refactoring

---

## ✅ VALIDATION CHECKLIST (FOR AI)

Before final output, the AI **MUST verify**:

-

---

## 🏁 FINAL DIRECTIVE

> **This document is a strict rule set, not a guideline.**

If any rule conflicts with convenience or style preferences, **the rule always wins**.

