# Clean Code Naming Conventions and Best Practices

**Context:** Use the following principles derived from "Clean Code" by Robert C. Martin (Chapter 2: Meaningful Names) as a strict guideline for code generation, refactoring, and review.

## 1. Core Philosophy: The Premise
*   **Code as English:** Code must read like pure English. It should be understandable even by non-programmers.
*   **Explicit over Implicit:** Clarity is paramount. Do not force the reader to guess the intent or perform mental mapping.
*   **Domain Language:** Always inject the "Business Logic" or "Domain Language" into the code. Use terms from the specific industry (e.g., Banking, E-commerce) to define elements.

## 2. Do's: Meaningful Naming Guidelines
*   **Intention-Revealing Names:** Names must tell why a variable exists, what it does, and how it is used. Avoid generic names like `list1`, `data`, or `x`.
*   **Parts of Speech:**
    *   **Variables, Constants, and Classes** must be **Nouns** or noun phrases representing concepts.
    *   **Methods and Functions** must be **Verbs** or verb phrases representing behaviors (e.g., `getAccount`, `isFlagged`).
*   **Pronounceable & Searchable:** Use names that can be easily spoken during team discussions. Avoid prefixes (like `acc_`) that make searching in an IDE difficult.
*   **Naming by Scope:**
    *   **Variable Name Length** should be **Directly Proportional** to its scope (Longer names for global/wider scopes).
    *   **Function Name Length** should be **Inversely Proportional** to its scope (Private, internal helper functions should have descriptive, longer names than high-level public ones).
*   **Standard Patterns:** Consistently use `getX`, `setX`, and `isX` (for booleans/predicates).

## 3. Don'ts: Anti-Patterns to Avoid
*   **Avoid Disinformation:** Do not provide false clues. Don't name a variable `accountList` if it is actually a Map or a Set.
*   **Never Use Abbreviations:** Do not sacrifice clarity for brevity. Use `temporary` instead of `tmp`, and `temperature` instead of `temp`.
*   **Avoid Small Variations:** Do not use names that vary in tiny ways (e.g., `XYZControllerForEfficientHandlingOfStrings` vs. `XYZControllerForEfficientStorageOfStrings`).
*   **Avoid Noise Words:** Remove redundant words like `NameString` (it’s obviously a string), `CustomerObject` (it’s an object), or `ProductData` (`data` is a noise word).
*   **Avoid Ambiguous Characters:** Never use `l` (lowercase L), `O` (uppercase O), or `I` (uppercase I) in contexts where they can be confused with `1` or `0`.
*   **Avoid Encoding:**
    *   Do not use Hungarian notation or member prefixes (e.g., `m_variable`).
    *   **Interfaces:** Do not add an "I" prefix to interfaces (e.g., use `Account` instead of `IAccount`).
*   **No Mental Mapping:** Do not use single-letter aliases (e.g., `CP` for `ConfigParser`). The reader should not have to memorize what a shortcut means.
*   **Don't Be Cute:** Avoid puns, jokes, or "inside-team" humor (e.g., `holyHandGrenade()` to kill a process). Be professional.

## 4. Abstraction and Implementation
*   **Hide Implementation Details:** Abstract the data types. Prefer names like `flaggedCells` over `cellArray`. Focus on the "What" rather than the "How".
*   **Replace Magic Numbers/Strings:** Never use raw numbers or strings in logic (e.g., `if (status == 4)`). Replace them with meaningful constants or boolean methods (e.g., `if (cell.isFlagged())`).
