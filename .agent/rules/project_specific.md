---
description: Project-specific rules for branch configuration, step execution, and data processing
---

# Project-Specific Rules

## Branch Configuration

### Branch Names
The project uses 6 branches defined in `src/core/domain/branches/config.py`:
- `admin`, `nujum`, `akba`, `shahid`, `asherin`, `wardani`

### Search Order
When searching for surplus, use the order defined in `get_search_order()`:
1. admin
2. nujum
3. akba
4. shahid
5. asherin
6. wardani

## Step Execution Flow

The project follows an 11-step workflow:
1. **Step 1**: Archive Previous Output (archives `data/output` into `data/archive` and clears output)
2. **Step 2**: Convert Excel to CSV
3. **Step 3**: Validate Data (date range + headers; removes date header row after validation)
4. **Step 4**: Sales Analysis
5. **Step 5**: Rename Columns (Arabic to English)
6. **Step 6**: Split by Branches (creates branch files and analytics)
7. **Step 7**: Generate Transfer Files
8. **Step 8**: Split Transfer Files by Product Type
9. **Step 9**: Convert Split Files to Excel
10. **Step 10**: Generate Analytics Reports
11. **Step 11**: Generate Combined Transfers (merged and separate)

### Step Handler Pattern
- Each step has a handler in `src/app/pipeline/step_{N}/`
- Handlers should accept `use_latest_file: bool = None` parameter
- Return `bool` indicating success/failure
- Provide clear user feedback via print statements

## Product Classification

### Categories
Products are classified into 6 categories:
- `tablets_and_capsules`
- `injections`
- `syrups`
- `creams`
- `sachets`
- `other`

### Classification Rules
- Check for specific keywords in product names (case-insensitive)
- Handle Arabic and English keywords
- Priority order matters (e.g., check "shampoo" before "amp" to avoid misclassification)

## Data Processing Rules

### Surplus Distribution Logic
1. Sort needing branches by `avg_sales` (descending) then `balance` (ascending)
2. Sort surplus branches by available surplus quantity (descending)
3. If total surplus < total needed, distribute proportionally
4. Track all withdrawals with numbered columns (`surplus_from_branch_1`, etc.)
5. Calculate `surplus_remaining` after all withdrawals

### File Naming Conventions
- Transfer files: `{base_name}_from_{source}_to_{target}.csv`
- Split files: `{base_folder_name}_{timestamp}_{category}.csv`
- Excel files: Same as CSV but with `.xlsx` extension
- Analytics files: `{base_filename}_{branch}_analytics.csv`

### Directory Structure
- Branch files: `data/output/{branch}/{filename}_{branch}.csv`
- Analytics: `data/output/analytics/{branch}/{filename}_{branch}_analytics.csv`
- Transfers: `data/output/transfers/transfers_from_{source}_to_other_branches/`
- Excel: `data/output/transfers_excel/transfers_excel_from_{source}_to_other_branches/`

## Date Header Handling

- Some CSV files have a date header as the first row
- Always check for date header using `extract_dates_from_header()`
- When writing files, conditionally include date header based on `has_date_header` flag
- Step 2 removes the date header row after validation

## Column Requirements

### Base Columns
All branch files must include:
- `code`, `product_name`, `selling_price`, `company`, `unit`
- `total_sales`, `total_product_balance`

### Analytics Columns
Analytics files include:
- Base: `code`, `product_name`, `sales`, `avg_sales`, `balance`
- Calculated: `monthly_quantity`, `surplus_quantity`, `needed_quantity`
- Withdrawal columns: `surplus_from_branch_{N}`, `available_branch_{N}`, etc.

### Transfer Columns
Transfer files include:
- `code`, `product_name`, `quantity_to_transfer`, `target_branch`
