# Clean Code Function Rules ✅

## Function Length Rules

1. **Keep functions very short** 🤏

   * Ideal: 4–5 lines (per Kent Beck).
   * Acceptable: 10–20 lines (per Uncle Bob).

2. **Line width limit** ✍️

   * Each line should not exceed 80 characters for readability.

## Code Block Rules (if, else, for, while) 🧱

3. **Single line per block**

   * Each block should contain only one line, usually a function call.
   * Benefit: reduces indentation depth and makes code understandable instantly ⚡

## Levels of Abstraction 💡

4. **What vs How**

   * High-level functions should describe *what* they do, not *how*. 🧐
   * Hide implementation details; let lower-level functions handle them. 🛡️
   * Use meaningful names for clarity at the top level.

## Refactoring Practices 🛠️

5. **Extract long conditions**

   * Move complex conditions to separate functions, e.g., `isValid()`. 🔍

6. **Separate responsibilities**

   * Avoid mixing logic; e.g., use `AcceptanceEvent` instead of embedding notifications. 📣

7. **Abstract UI/HTML code**

   * Encapsulate UI rendering in dedicated functions like `getSuccessView()`. 🖥️

8. **Early return / invert logic**

   * Use early exits (`if (!isValid) return;`) to reduce nesting. 🔄

9. **Reduce nested logic complexity** 🎯

   * **Maximum nesting depth: 2 levels**.
   * Extract nested blocks (3+ levels) into separate functions.
   * Use guards/early returns to flatten structure.
   * Example: Instead of `if A: if B: if C:` → Use `if not A: return` then `if B: if C:`

10. **Apply Command-Query Separation (CQS)**

   * **Command** (→ None): Change state, don't return data.
   * **Query** (→ data): Return data, don't change state.
   * Never mix both! ⚡

## Golden Rules / Guidelines ✨

11. **Step-down reading** 📖

   * Code should read top-to-bottom like a story; higher-level functions delegate to lower-level ones.

12. **Explicit is better than implicit** 💎

    * Always aim for clarity over clever tricks or hidden behavior.

13. **Readable for others** 🚀🏆

    * Anyone reading your code should understand the logic without digging into technical details.

## Function Arguments Rules 📊

14. **Number of Parameters** (The Numbers Rule)

    | Count | Type | Rating |
    |---|---|---|
    | **0** | Niladic | ✅ Ideal |
    | **1** | Monadic | ✅ Good |
    | **2** | Dyadic | ⚠️ Max limit |
    | **3+** | Polyadic | ❌ Refactor |

15. **Reduce Parameters via** 🛠️

    * **Parameter Object**: Group related data (dates → DateRange)
    * **Principle of Least Privilege**: Pass only what's needed, not whole objects
    * **Dependency Injection**: Let container resolve dependencies
    * **Factories**: Consolidate similar objects
    * **Extract Methods**: Move parameter logic to separate functions

16. **Forbidden Patterns** 🚫

    * **Boolean Parameters**: Split into separate functions (`process()` vs `process_with_tax()`)
    * **Pass by Reference**: Use immutability; avoid mutations
    * **Meta-programming/Reflection**: Too expensive; use type hints instead

17. **Why Reduce Parameters?** ✅

    * **Testing**: Fewer params = fewer test cases (0 params = 1 test; 3+ params = 20+ tests)
    * **Clarity**: Signature tells the whole story
    * **Maintainability**: Simple code = easier to change
