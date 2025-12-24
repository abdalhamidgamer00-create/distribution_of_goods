# 🏛️ Architectural Constitution

## Clean Architecture 🧼 + Domain-Driven Design (DDD) Rules for Distribution of Goods

> This document defines **strict, non-negotiable architectural rules**. Any violation introduces **explicit Technical Debt**.

---

## 🥇 Rule 0 — Domain Supremacy

**If a piece of code does not represent a clear business concept, it must not exist.**

- No "helper" code without domain meaning.
- Every module must answer: *What business responsibility do you represent?*
- Logic must be expressed in the "Language of the Pharmacist" (Domain Language).

---

## 1️⃣ Domain First Principle (Pure Python)

### Rule

**The Domain Layer is the core of the system and must be 100% Pure Python.**

- **Dependencies**: Zero external dependencies (except `typing` or `dataclasses`).
- **Forbidden**: Pandas, NumPy, Excel, CSV, Databases inside `src/domain`.
- **Infrastructure**: No file paths, environment access, or logging handlers.

---

## 2️⃣ Single Responsibility Rule (Strict)

### Rule

**Every module, class, and function must have exactly one reason to change.**

- Business logic → `src/domain`
- Use case flow → `src/application/use_cases`
- IO / Storage → `src/infrastructure`
- Orchestration → `src/application/pipeline`

---

## 3️⃣ Intentional Naming (No Step-Based Code)

### Rule

**Step-oriented naming in CODE is strictly prohibited, even if the business sees a "Step".**

- **Business Level**: "Step 1: Archive" is an orchestration sequence.
- **Code Level**: `ArchivePreviousOutput` is the implementation.
- **Forbidden**: `step_1.py`, `HandlerStep2`.
- **Required**: Intention-revealing names like `ShortageReporter`.

---

## 4️⃣ Explicit Dependencies Only

### Rule

**All dependencies must be explicitly declared and injected.**

- No globals.
- No shared mutable state across modules.
- Clear input/output contracts only.

---

## 5️⃣ No Infrastructure Leakage

### Rule

**Infrastructure details must never leak into inner layers.**

- DataFrames are an infrastructure detail for fast processing but should be mapped to Domain Entities when logic is applied.
- Inner layers must not know about Excel formats or CSV delimiters.

---

## 6️⃣ Code Quality: The 100/20/80 Rule

### Rule

**Code must be concise, readable, and fit on a standard screen.**

- **Files**: Max 100 lines of code.
- **Functions**: Max 20 lines of code.
- **Line Width**: Max 80 characters.
- *Violation requires extraction into a new sub-module.*

---

## 7️⃣ Zero Abbreviations Policy

### Rule

**All identifiers must be fully descriptive. Abbreviations are forbidden.**

- **Forbidden**: `admin`, `qty`, `src/utl`, `tmp`.
- **Required**: `administration`, `quantity`, `src/shared/utility`, `temporary`.

---

## 8️⃣ Import Safety: Absolute Path Mandate

### Rule

**All imports must use absolute project paths.**

- **Mandatory**: `from src.presentation.gui...`
- **Forbidden**: `from ..utils...` (Relative imports).
- *Rationale: Ensures compatibility with Streamlit's execution model and modular testing.*

---

## 9️⃣ Testability & Error Policy

### Rule

**Any untestable code is invalid. Silent failure is forbidden.**

- No IO in domain logic (allows pure unit tests).
- Deterministic logic only.
- Use explicit Domain Exceptions; never return `None` or `False` for errors.

---

## 🔟 Clear Layer Ownership

### Rule

**Every file belongs to exactly one layer. Cross-layer calls must go inward.**

- `src/presentation`: CLI, GUI, Views.
- `src/application`: Use Cases, Pipeline Orchestration, Ports.
- `src/domain`: Entities, Business Rules, Domain Services.
- `src/infrastructure`: Repositories, Converters, Adapters.
- `src/shared`: Generic Utilities (Non-Domain), Constants.

---

## 🧠 Final Law

**Architecture is defined by decisions that are expensive to change.**

---

## 📚 References

- Clean Architecture — Robert C. Martin
- Domain-Driven Design — Eric Evans
- Clean Code — Robert C. Martin (Naming & 100/20/80)
