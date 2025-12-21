---
description: Guidelines for when and how to refactor code in this project
---

# Refactoring Guidelines

## When to Refactor

- Files exceed 200-300 lines
- Functions exceed 50 lines
- Code duplication detected
- Complex nested logic (3+ levels)
- Multiple responsibilities in one module

## Refactoring Patterns

### Extract Functions
- Break large functions into smaller, focused functions
- Each function should do one thing well
- Functions should be testable in isolation

### Extract Modules
- Group related functions into modules
- Create subdirectories for logical groupings
- Use `__init__.py` to maintain backward compatibility

### Configuration Extraction
- Move constants to configuration files
- Use configuration classes/functions for settings
- Centralize branch names, column names, etc.

## Refactoring Process

1. **Read and Understand**: Read the entire file/module first
2. **Identify Responsibilities**: List what the code does
3. **Plan Structure**: Design the new modular structure
4. **Create New Modules**: Build new modules with clear purposes
5. **Update Imports**: Update all import statements
6. **Test**: Verify functionality is preserved
7. **Delete Old Code**: Remove old files only after verification

## Module Organization Examples

### Before (Large File)
```python
# file_splitter.py (200+ lines)
def split_file():
    # 50 lines of logic
    pass

def convert_to_excel():
    # 50 lines of logic
    pass
```

### After (Modular)
```
services/splitting/
├── __init__.py
└── file_splitter.py      # Only splitting logic

services/transfers/
├── __init__.py
└── excel_converter.py    # Only conversion logic
```

## Import Management

### Maintain Backward Compatibility
- Update `__init__.py` to re-export functions
- Keep old import paths working during transition
- Document migration path for deprecated imports

### Example
```python
# src/services/transfers/__init__.py
from src.services.transfers.splitters.file_splitter import split_all_transfer_files
from src.services.transfers.converters.excel_converter import convert_all_split_files_to_excel

__all__ = ['split_all_transfer_files', 'convert_all_split_files_to_excel']
```

## Testing After Refactoring

- Run all existing tests
- Verify output files match previous versions
- Check that all steps execute successfully
- Validate data integrity
