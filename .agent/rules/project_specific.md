---
description: Project-specific rules for branch configuration, step execution, and data processing
---

# Project-Specific Rules

## Clean Code Policies

### Zero Abbreviations Policy
All identifiers (variables, functions, classes, modules, directories) must be fully descriptive. Abbreviations are strictly forbidden.
- **Forbidden**: `admin`, `akba`, `nujum`, `src/core`, `tmp`, `util`.
- **Required**: `administration`, `okba`, `star`, `src/domain`, `temporary`, `utility`.

### 100/20/80 Rule
- **Files**: Must not exceed 100 lines of code.
- **Functions**: Must not exceed 20 lines of code.
- **Line Length**: Must not exceed 80 characters.

## Branch Configuration

### Branch Names
The project uses 6 branches defined in `src/domain/services/branches/config.py`:
- `administration`, `star`, `okba`, `shahid`, `asherin`, `wardani`

### Search Order
When searching for surplus, use the order defined in `get_search_order()`:
1. `administration`
2. `star`
3. `okba`
4. `shahid`
5. `asherin`
6. `wardani`

## Step Execution Flow

The project follows an 11-step workflow managed by `src/application/pipeline/steps.py`:
1. **Step 1**: Archive Previous Output
2. **Step 2**: Convert Excel to CSV
3. **Step 4**: Sales Analytics
4. **Step 5**: Schema Normalization (Rename Columns)
5. **Step 6**: Branch Segmentation
6. **Step 7**: Transfer Optimization
7. **Step 8**: Transfer Classification
8. **Step 9**: Surplus Reporting
9. **Step 10**: Shortage Reporting
10. **Step 11**: Combined Transfers (merged and separate)

## Product Classification

### Categories
Products are classified into 6 categories:
- `tablets_and_capsules`
- `injections`
- `syrups`
- `creams`
- `sachets`
- `other`

## Data Processing Rules

### Surplus Distribution Logic
1. Sort needing branches by `avg_sales` (descending) then `balance` (ascending).
2. Sort surplus branches by available surplus quantity (descending).
3. If total surplus < total needed, distribute proportionally.
4. Track withdrawals with numbered columns (`surplus_from_branch_1`, etc.).

### File Naming Conventions
- Transfer files: `{base_name}_from_{source}_to_{target}.csv`
- Combined files: `combined_transfers_from_{branch}_{timestamp}.csv`

## GUI Architecture

### Service-View-Renderer Pattern
The GUI follows a strict Service-View separation, often using Renderers for complex logic:
- **Services**: Pure logic (e.g., `src/presentation/gui/services/`).
- **Views**: Layout and orchestration (e.g., `src/presentation/gui/views/`).
- **Renderers**: Complex UI building logic (e.g., `merged_view_renderer.py`).

### Import Safety
**CRITICAL**: Always use absolute imports from `src.presentation.gui.*` within the GUI package. Relative imports (`from ..`) will fail under Streamlit's page execution model.
