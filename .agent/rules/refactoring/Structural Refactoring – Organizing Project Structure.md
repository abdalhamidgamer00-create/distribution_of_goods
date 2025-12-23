# 🏗️ Structural Refactoring – Organizing Project Structure

**Structural Refactoring** is the process of reorganizing the code, folders, and files in a project to create a clean, clear, and maintainable structure **without changing the program’s behavior**.

---

## 1️⃣ Main Goals
- Improve **maintainability**.  
- Reduce complexity and dependencies between files and modules.  
- Make it easier to **add new features** or modify existing code.  
- Enhance **testability** of individual parts of the code.

---

## 2️⃣ When to Apply Structural Refactoring
- The file or module is too large (>100–400 lines).  
- Code or structure is repeated across files.  
- Strong dependencies exist between different modules.  
- Project is hard to understand or extend.

---

## 3️⃣ Steps to Reorganize Project Structure

1. **Identify core units and responsibilities**:
   - Models (data representation)  
   - Services (business logic / operations)  
   - Controllers / Handlers (user interaction or API)  
   - Utils / Helpers (utility functions)

2. **Create separate folders for each unit**:
   ```
   project/
   ├─ models/
   │   └─ user.py
   ├─ services/
   │   ├─ user_service.py
   │   ├─ email_service.py
   └─ main.py
   ```

3. **Move files and code according to responsibility**:
   - Each class or function goes into the folder that represents its responsibility.

4. **Reduce dependencies between files**:
   - Use Dependency Injection or pass services as parameters.  
   - Avoid importing too many files directly.

5. **Eliminate structural duplication (Structural DRY)**:
   - If the same structure repeats in multiple modules, move it to a Base Class or Mixin.

6. **Apply Command-Query Separation (CQS)**:
   - Functions should either **perform an action (Command)** or **return data (Query)**, but not both.

### Example of CQS:
```python
# Command function (modifies state)
def add_item(cart, item):
    cart.append(item)

# Query function (returns value without side effects)
def cart_size(cart):
    return len(cart)
```
✅ This separation makes the code easier to understand, test, and maintain.

---

## 4️⃣ Practical Example Before & After

### Before Refactoring:
```python
# app.py
users = []

def add_user(name):
    users.append(name)
    print(f"Email sent to {name}")
```

### After Refactoring:
```
project/
├─ models/
│   └─ user.py
├─ services/
│   ├─ user_service.py
│   └─ email_service.py
└─ main.py
```

```python
# models/user.py
class User:
    def __init__(self, name):
        self.name = name

# services/user_service.py
def add_user(user, users):
    users.append(user)

# services/email_service.py
def send_email(user):
    print(f"Email sent to {user.name}")

# main.py
from models.user import User
from services.user_service import add_user
from services.email_service import send_email

users = []
user = User("Ali")
add_user(user, users)
send_email(user)
```

✅ Improvements:
- Each functionality is in the correct place.  
- Code is maintainable and easier to understand.  
- Each part can be tested independently.

---

## 5️⃣ Pro Tips
- Start with large and repetitive files.  
- Follow **SRP (Single Responsibility Principle)** – each unit should have one responsibility.  
- Apply **Structural DRY** to reduce duplicate structure.  
- Use **Command-Query Separation** to make functions predictable and testable.
- Test every change before and after refactoring.  
- Monitor module dependencies to avoid tight coupling.

---

> 💡 Remember: Structural Refactoring is not just about moving files. It’s about **improving the overall project design** to make it cleaner, more flexible, and scalable.

