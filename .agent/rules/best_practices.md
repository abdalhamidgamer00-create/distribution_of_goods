---
description: Best practices for code organization, data processing, and maintainability
---

# Best Practices

## Code Organization

### Modularity
- Break large files into smaller, focused modules
- Each module should have a single, clear responsibility
- Group related functionality in subdirectories
- Use `__init__.py` to expose public APIs

### Reusability
- Extract common logic into utility functions
- Avoid code duplication
- Use configuration files for constants (e.g., `branch_config.py`)
- Create helper functions for repeated operations

### Maintainability
- Write self-documenting code with clear variable names
- Add comments for complex business logic
- Keep functions small and focused
- Use type hints to improve code clarity

## Data Processing

### Pandas Best Practices
- Always use `.copy()` when creating DataFrame subsets
- Use vectorized operations when possible
- Avoid iterating with `.iterrows()` when vectorized operations are possible
- Handle NaN values explicitly
- Use `pd.notna()` for null checks

### File I/O
- Always specify encoding (`utf-8-sig` for CSV files)
- Use context managers for file operations
- Check file/directory existence before operations
- Handle file not found errors gracefully
- Preserve directory structure when creating output files

### Error Handling
```python
try:
    # Operation
    result = process_data()
    return result
except FileNotFoundError:
    print(f"File not found: {file_path}")
    return None
except Exception as e:
    print(f"Error processing: {e}")
    return None
```

## Testing Considerations

- Test edge cases (empty data, missing files, invalid inputs)
- Verify calculations with known test data
- Test file operations with various scenarios

## Performance

- Use vectorized pandas operations instead of loops
- Read files once and process in memory when possible
- Avoid unnecessary DataFrame copies
- Use appropriate data types to reduce memory usage

## Security

- Validate all user inputs
- Sanitize file paths to prevent directory traversal
- Don't execute user-provided code
- Handle sensitive data appropriately

## Documentation

- Document complex algorithms and business logic
- Explain why, not just what
- Update documentation when code changes
- Include examples in docstrings for complex functions
