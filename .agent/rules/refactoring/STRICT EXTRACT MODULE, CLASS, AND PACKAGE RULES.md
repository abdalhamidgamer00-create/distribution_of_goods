# 🧱 STRICT EXTRACT MODULE, CLASS, AND PACKAGE RULES (PYTHON)

This document defines **strict, non-negotiable rules** that an AI model **MUST follow** when performing code organization refactoring in a Python project, applying to all file types but especially to files containing more than 100 lines.

The purpose is **code organization only**.

❌ Do NOT change behavior\
❌ Do NOT refactor algorithms\
❌ Do NOT optimize performance\
❌ Do NOT introduce new features

---

## 🎯 SCOPE

These rules apply to all file types, with particular attention to files containing more than 100 lines, and cover:

- Extracting code into **new Python modules (files)**
- Extracting classes into separate modules
- Moving functions
- Extracting packages
- Enforcing proper dependency direction
- Improving logical separation and readability
- Applying **DRY principle** to avoid code duplication

These rules do **NOT** cover:

- Architecture redesign beyond dependencies
- Business logic changes
- Performance optimization
- Introducing new design patterns

---

## 🔒 HARD CONSTRAINTS (MANDATORY)

The AI model **MUST** obey all constraints below:

1. **Program behavior must remain identical**
2. **Public APIs must not change**
3. **No logic modification is allowed**
4. **No renaming unless explicitly instructed**
5. **No code deletion**
6. **Imports must remain valid and minimal**
7. **Each new module/class/package must have a single responsibility**
8. **Do not duplicate code across modules or classes (DRY principle)**

Violation of any rule is **NOT permitted**.

---

## 📦 EXTRACT MODULE RULES

A new module **MAY be created ONLY IF** one or more conditions apply:

- A file contains **multiple unrelated responsibilities**
- A group of functions operates on the **same concept or data**
- A section of code can be described with **one clear responsibility sentence**
- The extracted code can be reused without modification
- The extraction will **avoid code duplication** (DRY principle)

If none apply, extraction is **FORBIDDEN**.

---

## 🏗 EXTRACT CLASS RULES

A class **MUST be extracted** only if:

- It groups related functions and properties
- It can be isolated into a module with a **single responsibility**
- Extracting improves readability or maintainability
- Extraction will **avoid code duplication** (DRY principle)

Class extraction **MUST NOT**:

- Change visibility of functions or attributes
- Split behavior into unrelated modules

---

## 📦 EXTRACT PACKAGE RULES

A package **MUST be extracted** only if:

- Multiple modules share a cohesive responsibility
- It helps enforce clear folder-level separation
- Internal module dependencies remain logical and directed
- Extraction will **avoid code duplication** (DRY principle)

---

## 🔄 MOVE FUNCTION RULES

The AI model **MUST**:

- Move functions only to modules/classes where they belong logically
- Keep public functions public and private functions private
- Respect function ordering in the new module
- Never change the function logic
- Ensure no duplicated code occurs after moving functions (DRY principle)

---

## 🔗 DEPENDENCY DIRECTION RULES

- Dependencies must always point **downward** in the hierarchy
- Modules/packages **MUST NOT** depend on higher-level modules
- Circular dependencies are **strictly forbidden**
- Moving functions or classes must respect dependency direction

## 🔌 REDUCE DEPENDENCIES BETWEEN FILES

- Use **Dependency Injection**: pass services as parameters instead of importing.
- Avoid direct imports of multiple files; prefer interfaces/abstractions.
- Keep imports minimal: only import what you directly use.
- Limit file-to-file coupling to enable easier testing and maintenance.

---

## 📏 LINE LENGTH RULE

- Every line **MUST** be ≤ 80 characters
- Applies to:
  - Code
  - Docstrings
  - Comments

Only formatting may be changed to satisfy this rule.

---

## 🚫 FORBIDDEN ACTIONS

The AI model **MUST NOT**:

- Merge unrelated logic into a single module/package
- Extract trivial modules or classes without responsibility
- Break dependency rules
- Rename entities without instruction
- Change function or class behavior
- Introduce new abstraction layers unnecessarily
- Duplicate code across modules or classes (violating DRY principle)

---

## ✅ VALIDATION CHECKLIST (MANDATORY)

Before final output, the AI **MUST confirm**:

- testing by pytest 

---

## 🏁 FINAL DIRECTIVE

> **This document is a strict rule set, not a guideline.**

If any rule conflicts with convenience, style, or preference,\
**THE RULE ALWAYS WINS.**

