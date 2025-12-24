---
description: Project directory organization and module structure guidelines
---

# Project Structure Rules

## Directory Organization

This project follows a Clean Architecture with DDD principles, strictly separated into layers:

```
project_root/
├── src/
│   ├── presentation/            # Outer layer (User Interaction)
│   │   ├── cli/                 # CLI entry points and menus
│   │   └── gui/                 # Streamlit UI, views, and components
│   ├── application/             # Application Layer (Use Cases & Pipeline)
│   │   ├── pipeline/            # Workflow orchestration
│   │   ├── use_cases/           # Implementation of business workflows
│   │   └── ports/               # Port interfaces
│   ├── domain/                  # Heart of the system (Models & Business Logic)
│   │   ├── models/              # Pure domain entities
│   │   ├── services/            # Domain services (engines, calculators)
│   │   └── exceptions/          # Domain-specific exceptions
│   ├── infrastructure/          # Adapters (Technical implementations)
│   │   ├── repositories/        # Persistence adapters
│   │   ├── converters/          # File format adapters
│   │   ├── adapters/            # Other external adapters
│   │   └── excel/               # Excel-specific implementation details
│   └── shared/                  # Cross-cutting concerns
│       ├── utility/             # Generic tools
│       └── constants.py         # Global project constants
└── tests/                       # Project test suite
```

## Module Organization Principles

1. **Single Responsibility**: Each module has one clear business or technical purpose.
2. **Layered Isolation**: Inner layers (Domain) must never depend on outer layers (Presentation/Infrastructure).
3. **Domain Purity**: `src/domain` MUST remain 100% pure Python with zero external dependencies.
4. **100/20/80 Rule**: Mandatory adherence to line/function/file length limits.

## Naming Conventions

- **Clean Names**: `presentation` instead of `app`, `utility` instead of `utils`.
- **Zero Abbreviations**: Always use full descriptive names (e.g., `administration`).

## Import Organization

Always use absolute imports (`from src.*`). 

**CRITICAL**: Absolute imports are mandatory for Streamlit subpage compatibility.
