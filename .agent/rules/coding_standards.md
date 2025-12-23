---
description: Python coding standards including formatting, documentation, and naming conventions
---

# Coding Standards

## Python Style Guide

### Code Formatting
- Follow PEP 8 style guide
- Use 4 spaces for indentation (no tabs)
- Maximum line length: 80 characters
- Use type hints for function parameters and return values

### Function Definitions
```python
def function_name(param1: str, param2: int = 0) -> dict:
    """
    Clear docstring explaining the function's purpose.
    
    Args:
        param1: Description of param1
        param2: Description of param2 (default: 0)
        
    Returns:
        Description of return value
        
    Raises:
        ValueError: When invalid input is provided
    """
    # Implementation
    pass
```

### Error Handling
- Always use try-except blocks for file operations
- Provide meaningful error messages
- Log errors appropriately
- Return None or empty dict/list on failure (document this behavior)

### Data Handling
- Always use `encoding='utf-8-sig'` for CSV files
- Use `pd.read_csv()` with proper encoding
- Handle missing values explicitly with `pd.notna()` checks
- Use `.copy()` when modifying DataFrames to avoid SettingWithCopyWarning

### File Operations
- Always check if directories exist before writing
- Use `os.makedirs(path, exist_ok=True)` for directory creation
- Close file handles properly or use context managers
- Include date headers when `has_date_header=True`

### Naming Conventions
- Variables: `snake_case`
- Functions: `snake_case`
- Classes: `PascalCase`
- Constants: `UPPER_SNAKE_CASE`
- Private functions: `_leading_underscore`

### Documentation
- All public functions must have docstrings
- Use Google-style docstrings
- Document all parameters and return values
- Include examples for complex functions
