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

## Golden Rules / Guidelines ✨

9. **Step-down reading** 📖

   * Code should read top-to-bottom like a story; higher-level functions delegate to lower-level ones.

10. **Explicit is better than implicit** 💎

    * Always aim for clarity over clever tricks or hidden behavior.

11. **Readable for others** 🚀🏆

    * Anyone reading your code should understand the logic without digging into technical details.
