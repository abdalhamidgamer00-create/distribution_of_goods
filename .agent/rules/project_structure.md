---
description: Project directory organization and module structure guidelines
---

# Project Structure Rules

## Directory Organization

This project follows a modular architecture with clear separation of concerns, organized
into application, domain, services, and shared layers:

```
project_root/
├── src/
│   ├── app/                     # Application layer (CLI + pipeline orchestration)
│   │   ├── cli/                 # Command-line interface and menus
│   │   └── pipeline/            # Step handlers (step_1 .. step_11, steps.py)
│   ├── core/                    # Core domain logic and validation
│   │   ├── domain/
│   │   │   ├── analysis/        # Data analysis modules
│   │   │   ├── branches/        # Branch configuration and helpers
│   │   │   ├── calculations/    # Distribution and quantity calculations
│   │   │   └── classification/  # Product classification logic
│   │   └── validation/          # Data validation (CSV headers, dates, etc.)
│   ├── services/                # Application services (I/O heavy / orchestration helpers)
│   │   ├── conversion/          # File format conversion + column mapping
│   │   ├── splitting/           # Branch splitting pipeline (processors + writers)
│   │   └── transfers/           # Transfer file generation, splitting, and Excel export
│   └── shared/                  # Shared cross-cutting utilities
│       ├── utils/               # Logging, file handling, archiver, etc.
│       ├── dataframes/          # DataFrame helpers (validators, cleaning)
│       └── reporting/           # Report generation utilities
└── tests/                       # Test scripts (at project root, not inside src)
```

## Module Organization Principles

1. **Single Responsibility**: Each module should have one clear purpose
2. **Separation of Concerns**: Business logic separated from I/O operations
3. **Modularity**: Related functions grouped into subdirectories
4. **Clear Naming**: Module names should clearly indicate their purpose

## File Naming Conventions

- Use snake_case for all file names
- Handler files: `step_{N}_handler.py`
- Generator files: `{purpose}_generator.py`
- Processor files: `{purpose}_processor.py`
- Calculator files: `{purpose}_calculator.py`
- Writer files: `{purpose}_writer.py`

## Import Organization

1. Standard library imports
2. Third-party imports
3. Local application imports (from src.*)

Always use absolute imports from `src.*` for clarity.
