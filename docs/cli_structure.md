# CLI Module Structure

## Overview
The CLI module has been organized into a clear hierarchical structure with internal directories for better organization and maintainability.

## Directory Structure

```
src/app/cli/
├── __init__.py              # Main exports (run_menu)
├── menu.py                  # Main entry point (8 lines)
├── core/                    # Core components
│   ├── __init__.py          # Core exports
│   ├── constants.py         # Shared constants
│   └── controller.py        # Menu control logic
├── ui/                      # User interface
│   ├── __init__.py          # UI exports
│   └── display.py           # Menu display
├── handlers/                # Input handling
│   ├── __init__.py          # Handler exports
│   └── input_handler.py    # User input processing
└── executors/               # Step execution
    ├── __init__.py          # Executor exports
    ├── step_executor.py    # Single step execution
    └── batch_executor.py   # Batch execution
```

## Module Responsibilities

### `core/` - Core Components
**Purpose**: Core functionality and shared constants

- **`constants.py`**: 
  - `SEPARATOR` - Menu separator string
  - `EXIT_CHOICE` - Exit option value
  - `ALL_STEPS_CHOICE_OFFSET` - All steps option number

- **`controller.py`**: 
  - `is_exit_choice()` - Check if exit chosen
  - `is_all_steps_choice()` - Check if all steps chosen
  - `is_valid_step_choice()` - Validate step choice
  - `handle_user_choice()` - Process user choice

### `ui/` - User Interface
**Purpose**: Display and presentation

- **`display.py`**: 
  - `display_menu()` - Show main menu with all options

### `handlers/` - Input Handling
**Purpose**: User input processing

- **`input_handler.py`**: 
  - `get_user_choice()` - Get menu selection
  - `get_file_selection_mode()` - Get file selection preference

### `executors/` - Step Execution
**Purpose**: Execute pipeline steps

- **`step_executor.py`**: 
  - `find_step_by_id()` - Find step by ID
  - `validate_step_function()` - Validate step function
  - `execute_single_step()` - Execute single step
  - `execute_step()` - Public API for step execution

- **`batch_executor.py`**: 
  - `log_step_progress()` - Log progress
  - `execute_all_steps_batch()` - Execute all steps
  - `display_execution_summary()` - Show summary
  - `execute_all_steps()` - Public API for batch execution

### Root Files
- **`menu.py`**: Main menu loop (only 8 lines!)
- **`__init__.py`**: Module exports

## Benefits

1. **Clear Organization**: Related files grouped in logical directories
2. **Easy Navigation**: Find files quickly by purpose
3. **Better Scalability**: Easy to add new components
4. **Separation of Concerns**: Each directory has a clear purpose
5. **Maintainability**: Changes isolated to specific directories

## Usage

```python
from src.app.cli.menu import run_menu

# Start the menu
run_menu()
```

Or use individual components:

```python
from src.app.cli.ui.display import display_menu
from src.app.cli.core.controller import handle_user_choice
from src.app.cli.executors import execute_step

display_menu()
handle_user_choice("1")
execute_step("1")
```

## Import Paths

All imports use the new structure:

```python
# Core components
from src.app.cli.core.constants import SEPARATOR
from src.app.cli.core.controller import handle_user_choice

# UI components
from src.app.cli.ui.display import display_menu

# Handlers
from src.app.cli.handlers.input_handler import get_user_choice

# Executors
from src.app.cli.executors import execute_step, execute_all_steps
```
