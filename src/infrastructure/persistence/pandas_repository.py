"""Pandas implementation of the DataRepository interface."""

import os
import pandas as pd
from typing import List, Dict, Optional
from src.domain.models.entities import (
    Product, Branch, StockLevel, ConsolidatedStock, BranchStock
)
from src.domain.models.distribution import Transfer, DistributionResult
from src.infrastructure.persistence.mappers import StockMapper
from src.shared.utils.logging_utils import get_logger
from src.shared.utils.file_handler import ensure_directory_exists
from src.shared.constants import BRANCHES
from src.application.interfaces.repository import DataRepository
from src.core.validation.dates import extract_dates_from_header

logger = get_logger(__name__)


class PandasDataRepository(DataRepository):
    """
    Handles data persistence using Pandas and local CSV files.
    """

    def __init__(self, input_dir: str, output_dir: str, **kwargs):
        self._input_dir = input_dir
        self._output_dir = output_dir
        self._surplus_dir = kwargs.get('surplus_dir', output_dir)
        self._shortage_dir = kwargs.get('shortage_dir', output_dir)
        self._analytics_dir = kwargs.get('analytics_dir', output_dir)

    def load_branches(self) -> List[Branch]:
        return [Branch(name=name) for name in BRANCHES]

    def load_products(self) -> List[Product]:
        consolidated = self.load_consolidated_stock()
        return [item.product for item in consolidated]

    def _read_csv_with_header_detection(self, file_path: str) -> pd.DataFrame:
        """Reads CSV and handles optional 1-line date header using domain logic."""
        with open(file_path, 'r', encoding='utf-8-sig') as f:
            first_line = f.readline().strip()
        
        # Use domain logic for date header detection
        start_date, end_date = extract_dates_from_header(first_line)
        
        if start_date and end_date:
            logger.info(f"Detected date header in {file_path}, skipping first line.")
            return pd.read_csv(file_path, skiprows=1, encoding='utf-8-sig')
        
        # Fallback: Check for typical "Unnamed" artifacts if read incorrectly
        df = pd.read_csv(file_path, encoding='utf-8-sig', nrows=5)
        if df.columns[0].startswith('Unnamed') or 'الفترة من' in df.columns[0]:
            logger.warning(f"Detected potential malformed header in {file_path}, retrying with skip.")
            return pd.read_csv(file_path, skiprows=1, encoding='utf-8-sig')

        return pd.read_csv(file_path, encoding='utf-8-sig')

    def load_consolidated_stock(self) -> List[ConsolidatedStock]:
        """Loads and maps consolidated stock from the latest input CSV."""
        if not os.path.exists(self._input_dir):
            return []
            
        files = [
            f for f in os.listdir(self._input_dir) 
            if f.endswith('.csv') and 'renamed' in f.lower()
        ]
        
        if not files:
            files = [f for f in os.listdir(self._input_dir) if f.endswith('.csv')]
            
        if not files:
            return []
            
        files.sort(
            key=lambda x: os.path.getmtime(os.path.join(self._input_dir, x)),
            reverse=True
        )
        
        csv_path = os.path.join(self._input_dir, files[0])
        num_days = 90 
        
        try:
            df = self._read_csv_with_header_detection(csv_path)
            # Ensure column names are stripped of whitespace and BOM
            df.columns = [c.strip().replace('\ufeff', '') for c in df.columns]
            
            logger.info(f"Loaded CSV from {csv_path} with columns: {list(df.columns)}")
            
            if 'code' not in df.columns:
                logger.error(f"CRITICAL: 'code' column missing in {csv_path}!")
                # Try to find a column that looks like 'code'
                for col in df.columns:
                    if 'code' in col.lower() or 'كود' in col:
                        logger.warning(f"Found potential match: '{col}'")

            results = []
            for _, row in df.iterrows():
                obj = StockMapper.to_consolidated_stock(row, num_days)
                if obj:
                    results.append(obj)
            return results
        except Exception as e:
            logger.error(f"Error loading consolidated stock from {csv_path}: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return []

    def save_branch_stocks(self, branch: Branch, stocks: List[BranchStock]) -> None:
        """Saves branch-specific stock levels to CSV."""
        df = StockMapper.to_branch_dataframe(stocks)
        
        branch_dir = os.path.join(self._analytics_dir, branch.name)
        os.makedirs(branch_dir, exist_ok=True)
        
        output_path = os.path.join(branch_dir, f"main_analysis_{branch.name}.csv")
        df.to_csv(output_path, index=False, encoding='utf-8-sig')

    def load_stock_levels(self, branch: Branch) -> Dict[str, StockLevel]:
        """Loads stock levels for a specific branch."""
        file_name = f"main_analysis_{branch.name}.csv"
        file_path = os.path.join(self._analytics_dir, branch.name, file_name)
        
        if not os.path.exists(file_path):
            logger.warning(f"Stock levels file not found for branch {branch.name}: {file_path}")
            return {}
            
        try:
            df = pd.read_csv(file_path, encoding='utf-8-sig')
            stocks = {}
            for _, row in df.iterrows():
                # Flexible column name lookup
                code_col = 'code' if 'code' in row else 'كود'
                if code_col in row:
                    stocks[str(row[code_col])] = StockMapper.to_stock_level(row)
            return stocks
        except Exception as e:
            print(f"Error loading stock levels for {branch.name}: {e}")
            return {}

    def save_transfers(self, transfers: List[Transfer]) -> None:
        """Saves transfers to CSV, grouped by source and target branch."""
        # Group by (src, tgt)
        pairs = {}
        for t in transfers:
            key = (t.from_branch.name, t.to_branch.name)
            if key not in pairs:
                pairs[key] = []
            pairs[key].append(t)
            
        os.makedirs(self._output_dir, exist_ok=True)
        
        for (src, tgt), ts in pairs.items():
            data = []
            for t in ts:
                data.append({
                    'code': t.product.code,
                    'product_name': t.product.name,
                    'quantity_to_transfer': t.quantity,
                    'target_branch': tgt
                })
            
            df = pd.DataFrame(data)
            df = df.sort_values(by='product_name')
            
            # Subdirectory for Step 11 compatibility
            subdir = f"transfers_from_{src}_to_other_branches"
            src_dir = os.path.join(self._output_dir, subdir)
            os.makedirs(src_dir, exist_ok=True)
            
            file_name = f"{src}_to_{tgt}.csv"
            output_path = os.path.join(src_dir, file_name)
            df.to_csv(output_path, index=False, encoding='utf-8-sig')

    def save_remaining_surplus(self, results: List[DistributionResult]) -> None:
        """Saves products with remaining surplus to per-branch (total) and per-category files."""
        from src.core.domain.classification.product_classifier import classify_product_type
        from datetime import datetime
        
        timestamp = datetime.now().strftime("%Y%m%d")
        base_dir = self._surplus_dir
        if base_dir.endswith('csv'):
            base_dir = os.path.dirname(base_dir)

        # Group data by Branch -> Category
        grouped_data = {}
        for res in results:
            for branch_name, surplus in res.remaining_branch_surplus.items():
                if surplus > 0:
                    category = classify_product_type(res.product.name)
                    if branch_name not in grouped_data:
                        grouped_data[branch_name] = {}
                    if category not in grouped_data[branch_name]:
                        grouped_data[branch_name][category] = []
                    
                    grouped_data[branch_name][category].append({
                        'code': res.product.code,
                        'product_name': res.product.name,
                        'remaining_surplus': surplus
                    })

        for branch_name, categories in grouped_data.items():
            all_branch_items = []
            for category, items in categories.items():
                all_branch_items.extend(items)
                df = pd.DataFrame(items).sort_values('product_name', key=lambda x: x.str.lower())
                
                # CSV Output: base/csv/branch/surplus_branch_category_date.csv
                csv_dir = os.path.join(base_dir, "csv", branch_name)
                os.makedirs(csv_dir, exist_ok=True)
                csv_path = os.path.join(csv_dir, f"remaining_surplus_{branch_name}_{category}_{timestamp}.csv")
                df.to_csv(csv_path, index=False, encoding='utf-8-sig')
                
                # Excel Output
                excel_dir = os.path.join(base_dir, "excel", branch_name)
                os.makedirs(excel_dir, exist_ok=True)
                excel_path = os.path.join(excel_dir, f"remaining_surplus_{branch_name}_{category}_{timestamp}.xlsx")
                df.to_excel(excel_path, index=False)
            
            # Save Total Branch File (All Categories)
            if all_branch_items:
                df_total = pd.DataFrame(all_branch_items).sort_values('product_name', key=lambda x: x.str.lower())
                csv_path_total = os.path.join(base_dir, "csv", branch_name, f"remaining_surplus_{branch_name}_total_{timestamp}.csv")
                df_total.to_csv(csv_path_total, index=False, encoding='utf-8-sig')
                
                excel_path_total = os.path.join(base_dir, "excel", branch_name, f"remaining_surplus_{branch_name}_total_{timestamp}.xlsx")
                df_total.to_excel(excel_path_total, index=False)

    def save_shortage_report(self, results: List[DistributionResult]) -> None:
        """Saves products with a net shortage to total and category-split files."""
        from src.core.domain.classification.product_classifier import classify_product_type
        from datetime import datetime
        from src.shared.constants import BRANCHES
        from src.app.gui.utils.translations import BRANCH_NAMES, COLUMNS
        
        timestamp = datetime.now().strftime("%Y%m%d")
        base_dir = self._shortage_dir
        if base_dir.endswith('csv'):
            base_dir = os.path.dirname(base_dir)

        # Helper to format items with balances and sales
        def format_item(res: DistributionResult):
            item = {
                COLUMNS['code']: res.product.code,
                COLUMNS['product_name']: res.product.name,
                COLUMNS['shortage_quantity']: res.remaining_needed,
                COLUMNS['total_sales']: res.total_sales
            }
            # Add balance for each branch
            for branch in BRANCHES:
                col_name = f"رصيد {BRANCH_NAMES.get(branch, branch)}"
                item[col_name] = res.branch_balances.get(branch, 0.0) if res.branch_balances else 0.0
            return item

        # Group data by Category
        grouped_data = {}
        all_shortage_items = []
        for res in results:
            if res.remaining_needed > 0:
                category = classify_product_type(res.product.name)
                formatted = format_item(res)
                all_shortage_items.append(formatted)
                
                if category not in grouped_data:
                    grouped_data[category] = []
                grouped_data[category].append(formatted)

        for category, items in grouped_data.items():
            df = pd.DataFrame(items).sort_values(COLUMNS['shortage_quantity'], ascending=False)
            
            # CSV Output
            csv_dir = os.path.join(base_dir, "csv")
            os.makedirs(csv_dir, exist_ok=True)
            csv_path = os.path.join(csv_dir, f"total_shortage_{category}_{timestamp}.csv")
            df.to_csv(csv_path, index=False, encoding='utf-8-sig')
            
            # Excel Output
            excel_dir = os.path.join(base_dir, "excel")
            os.makedirs(excel_dir, exist_ok=True)
            excel_path = os.path.join(excel_dir, f"total_shortage_{category}_{timestamp}.xlsx")
            df.to_excel(excel_path, index=False)

        # Save Consolidated Total File (All Categories)
        if all_shortage_items:
            df_total = pd.DataFrame(all_shortage_items).sort_values(COLUMNS['shortage_quantity'], ascending=False)
            csv_path_total = os.path.join(base_dir, "csv", f"shortage_report_total_{timestamp}.csv")
            df_total.to_csv(csv_path_total, index=False, encoding='utf-8-sig')
            
            excel_path_total = os.path.join(base_dir, "excel", f"shortage_report_total_{timestamp}.xlsx")
            df_total.to_excel(excel_path_total, index=False)

    def load_transfers(self) -> List[Transfer]:
        """Loads transfers from the output directory (Step 7 output)."""
        transfers = []
        if not os.path.exists(self._output_dir):
            return []
            
        for root, _, files in os.walk(self._output_dir):
            for file in files:
                # Expecting src_to_tgt.csv or similar
                if file.endswith('.csv') and '_to_' in file:
                    # Skip already split files (e.g. category files)
                    if any(cat in file for cat in ["tablets", "injections", "syrups", "creams", "sachets", "other"]):
                        continue
                        
                    path = os.path.join(root, file)
                    base = os.path.splitext(file)[0]
                    
                    # More robust parsing for src_to_tgt
                    # Format can be src_to_tgt or transfers_from_src_to_other_branches/...
                    parts = base.split('_to_')
                    if len(parts) >= 2:
                        # Take the immediate parts around '_to_'
                        src_name = parts[0].split('_')[-1]
                        tgt_name = parts[1].split('_')[0]
                        
                        try:
                            df = self._read_csv_with_header_detection(path)
                            for _, row in df.iterrows():
                                transfers.append(Transfer(
                                    product=Product(code=str(row['code']), name=row['product_name']),
                                    from_branch=Branch(name=src_name),
                                    to_branch=Branch(name=tgt_name),
                                    quantity=int(row['quantity_to_transfer'])
                                ))
                        except Exception as e:
                            print(f"Error loading transfers from {path}: {e}")
        return transfers

    def save_split_transfers(self, transfers: List[Transfer], excel_dir: str) -> None:
        """Saves transfers split by product category into CSV and Excel."""
        from src.core.domain.classification.product_classifier import classify_product_type
        from datetime import datetime
        
        # Group by (src, tgt, category)
        groups = {}
        for t in transfers:
            category = classify_product_type(t.product.name)
            key = (t.from_branch.name, t.to_branch.name, category)
            if key not in groups:
                 groups[key] = []
            groups[key].append(t)
            
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        for (src, tgt, cat), ts in groups.items():
            data = []
            for t in ts:
                # Re-add product_type for Excel if needed (legacy had it sometimes)
                data.append({
                    'code': t.product.code,
                    'product_name': t.product.name,
                    'quantity_to_transfer': t.quantity,
                    'target_branch': tgt
                })
            df = pd.DataFrame(data).sort_values('product_name')
            
            # CSV: data/output/transfers/csv/src_to_tgt/src_to_tgt_timestamp_category.csv
            csv_subdir = os.path.join(self._output_dir, f"{src}_to_{tgt}")
            os.makedirs(csv_subdir, exist_ok=True)
            
            filename = f"{src}_to_{tgt}_{timestamp}_{cat}"
            csv_path = os.path.join(csv_subdir, f"{filename}.csv")
            df.to_csv(csv_path, index=False, encoding='utf-8-sig')
            
            # Excel: data/output/transfers/excel/transfers_excel_from_src_to_other_branches/src_to_tgt/src_to_tgt_timestamp_category.xlsx
            excel_subdir = os.path.join(
                excel_dir, 
                f"transfers_excel_from_{src}_to_other_branches", 
                f"{src}_to_{tgt}"
            )
            os.makedirs(excel_subdir, exist_ok=True)
            excel_path = os.path.join(excel_subdir, f"{filename}.xlsx")
            
            try:
                with pd.ExcelWriter(excel_path, engine='openpyxl') as writer:
                    df.to_excel(writer, index=False, sheet_name='Sheet1')
            except Exception as e:
                 print(f"Error saving Excel {excel_path}: {e}")

    def load_remaining_surplus(self, branch: Branch) -> List[Dict]:
        """Loads remaining surplus for a branch (Step 9 output)."""
        # Step 9 saves to surplus_dir/branch_name/remaining_surplus_branch.csv
        branch_dir = os.path.join(self._surplus_dir, branch.name)
        if not os.path.exists(branch_dir):
            return []
            
        data = []
        for file in os.listdir(branch_dir):
            if file.endswith('.csv') and 'remaining_surplus' in file:
                path = os.path.join(branch_dir, file)
                try:
                    df = pd.read_csv(path, encoding='utf-8-sig')
                    for _, row in df.iterrows():
                        data.append({
                            'code': str(row['code']),
                            'product_name': row['product_name'],
                            'quantity': int(row['remaining_surplus']),
                            'target_branch': 'admin',
                            'transfer_type': 'surplus'
                        })
                except Exception as e:
                    print(f"Error loading surplus from {path}: {e}")
        return data

    def save_combined_transfers(
        self, 
        branch: Branch,
        merged_data: List[Dict], 
        separate_data: List[Dict],
        timestamp: str
    ) -> None:
        """Saves combined transfers with Excel formatting."""
        # merged_data: list of {category: df}
        # separate_data: list of {target: {category: df}}
        
        base_dir = "data/output/combined_transfers"
        
        # Merged Output
        merged_csv_dir = os.path.join(base_dir, "merged", "csv", f"combined_transfers_from_{branch.name}_{timestamp}")
        merged_excel_dir = os.path.join(base_dir, "merged", "excel", f"combined_transfers_from_{branch.name}_{timestamp}")
        
        for item in merged_data:
            cat = item['category']
            df = item['df']
            os.makedirs(merged_csv_dir, exist_ok=True)
            csv_path = os.path.join(merged_csv_dir, f"{branch.name}_combined_{cat}.csv")
            df.to_csv(csv_path, index=False, encoding='utf-8-sig')
            
            os.makedirs(merged_excel_dir, exist_ok=True)
            excel_path = os.path.join(merged_excel_dir, f"{branch.name}_combined_{cat}.xlsx")
            self._save_formatted_excel(df, excel_path)
            
        # Separate Output
        sep_csv_dir = os.path.join(base_dir, "separate", "csv", f"transfers_from_{branch.name}_{timestamp}")
        sep_excel_dir = os.path.join(base_dir, "separate", "excel", f"transfers_from_{branch.name}_{timestamp}")
        
        for item in separate_data:
            target = item['target']
            cat = item['category']
            df = item['df']
            
            target_csv_dir = os.path.join(sep_csv_dir, f"to_{target}")
            os.makedirs(target_csv_dir, exist_ok=True)
            csv_path = os.path.join(target_csv_dir, f"transfer_from_{branch.name}_to_{target}_{cat}_{timestamp}.csv")
            df.to_csv(csv_path, index=False, encoding='utf-8-sig')
            
            target_excel_dir = os.path.join(sep_excel_dir, f"to_{target}")
            os.makedirs(target_excel_dir, exist_ok=True)
            excel_path = os.path.join(target_excel_dir, f"transfer_from_{branch.name}_to_{target}_{cat}_{timestamp}.xlsx")
            self._save_formatted_excel(df, excel_path)

    def _save_formatted_excel(self, df: pd.DataFrame, path: str) -> None:
        """Saves DataFrame to Excel with Step 11 styling."""
        from openpyxl.styles import PatternFill, Font, Alignment, Border, Side
        from openpyxl.formatting.rule import ColorScaleRule
        from openpyxl.utils import get_column_letter

        try:
            with pd.ExcelWriter(path, engine='openpyxl') as writer:
                df.to_excel(writer, index=False, sheet_name='Sheet1')
                workbook = writer.book
                worksheet = writer.sheets['Sheet1']
                
                # Header Styling
                header_fill = PatternFill(start_color="4472C4", end_color="4472C4", fill_type="solid")
                header_font = Font(bold=True, color="FFFFFF")
                for cell in worksheet[1]:
                    cell.fill = header_fill
                    cell.font = header_font
                    cell.alignment = Alignment(horizontal='center')
                    
                # Column Widths
                width_map = {
                    'code': 12, 'product_name': 40, 'quantity_to_transfer': 15, 
                    'sender_balance': 15, 'receiver_balance': 15, 
                    'target_branch': 15, 'transfer_type': 15
                }
                for i, col in enumerate(df.columns, 1):
                    letter = get_column_letter(i)
                    worksheet.column_dimensions[letter].width = width_map.get(col, 12)
                    
                # Borders
                thin = Side(style='thin')
                border = Border(left=thin, right=thin, top=thin, bottom=thin)
                for row in worksheet.iter_rows(min_row=1, max_row=len(df)+1, max_col=len(df.columns)):
                    for cell in row:
                        cell.border = border
                        
                # Color Scale for balances
                rule = ColorScaleRule(
                    start_type='num', start_value=0, start_color='FF0000',
                    mid_type='num', mid_value=15, mid_color='FFFF00',
                    end_type='num', end_value=30, end_color='00FF00'
                )
                for i, col in enumerate(df.columns, 1):
                    if col in ['sender_balance', 'receiver_balance']:
                        letter = get_column_letter(i)
                        worksheet.conditional_formatting.add(f"{letter}2:{letter}{len(df)+1}", rule)
                        
        except Exception as e:
            print(f"Error saving formatted Excel {path}: {e}")

    def list_outputs(self, category: str, branch_name: Optional[str] = None) -> List[Dict]:
        """Lists available output artifacts for a given category and optional branch."""
        # mapping category to (base_dir, patterns)
        # patterns: {format: prefix_pattern}
        mapping = {
            'transfers': {
                'base': self._output_dir,
                'patterns': {'csv': '', 'excel': ''}
            },
            'surplus': {
                'base': self._surplus_dir,
                'patterns': {'csv': '', 'excel': ''}
            },
            'shortage': {
                'base': self._shortage_dir,
                'patterns': {'csv': '', 'excel': ''}
            },
            'merged': {
                'base': os.path.join("data", "output", "combined_transfers", "merged"),
                'patterns': {'csv': 'combined_transfers_from_', 'excel': 'combined_transfers_from_'}
            },
            'separate': {
                'base': os.path.join("data", "output", "combined_transfers", "separate"),
                'patterns': {'csv': 'transfers_from_', 'excel': 'transfers_from_'}
            }
        }
        
        if category not in mapping:
            return []
            
        cfg = mapping[category]
        base_dir = cfg['base']
        results = []

        # Check for csv and excel subfolders
        for fmt in ['csv', 'excel']:
            fmt_dir = os.path.join(base_dir, fmt)
            if not os.path.exists(fmt_dir):
                # Fallback to base_dir if it's already a format dir (backward compatibility)
                if base_dir.endswith(fmt):
                    fmt_dir = base_dir
                else:
                    continue
            
            prefix = cfg['patterns'].get(fmt, '')
            sub_pattern = f"{prefix}{branch_name}" if branch_name else prefix
            
            # Special case for shortage (usually flat)
            if category == 'shortage':
                self._collect_files_recursive(fmt_dir, category, None, results)
                continue

            # Nested search for other categories
            for item in os.listdir(fmt_dir):
                item_path = os.path.join(fmt_dir, item)
                if not os.path.isdir(item_path):
                    continue
                    
                # Robust source branch matching for transfers
                is_match = sub_pattern in item
                if category == 'transfers' and branch_name:
                    is_match = (
                        item.startswith(branch_name) or 
                        f"from_{branch_name}" in item or
                        f"From_{branch_name}" in item
                    )
                
                if is_match:
                    # For 'separate', we have another level 'to_TARGET'
                    if category == 'separate':
                        for target_dir in os.listdir(item_path):
                            target_path = os.path.join(item_path, target_dir)
                            if os.path.isdir(target_path) and target_dir.startswith('to_'):
                                branch_meta = branch_name or item.split('_')[-1]
                                self._collect_files_recursive(target_path, category, branch_meta, results)
                    else:
                        branch_meta = branch_name or item
                        # For transfers, extract source branch from folder name if not provided
                        if category == 'transfers' and not branch_name:
                            # pattern: transfers_from_SOURCE_to_... or transfers_excel_from_SOURCE_to_...
                            if 'from_' in item and '_to_' in item:
                                branch_meta = item.split('from_')[1].split('_to_')[0]
                        
                        self._collect_files_recursive(item_path, category, branch_meta, results)
                        
        return results

    def _collect_files_recursive(self, directory: str, category: str, branch: Optional[str], results: List[Dict]) -> None:
        """Helper to collect files recursively and add metadata."""
        if not os.path.exists(directory):
            return
            
        # Get the immediate folder name for zip paths
        folder_name = os.path.basename(directory)
            
        for item in os.listdir(directory):
            path = os.path.join(directory, item)
            if os.path.isdir(path):
                # Recurse into subdirectory
                self._collect_files_recursive(path, category, branch, results)
            elif os.path.isfile(path) and item.endswith(('.csv', '.xlsx')):
                metadata = {
                    'name': item,
                    'path': os.path.abspath(path),
                    'size': os.path.getsize(path),
                    'mtime': os.path.getmtime(path),
                    'category': category,
                    'branch': branch,
                    'folder_name': folder_name
                }
                
                # Extract extra metadata for separate transfers
                if category == 'separate':
                    # directory format: .../csv/transfers_from_SOURCE_TS/to_TARGET
                    metadata['source_folder'] = os.path.basename(os.path.dirname(directory))
                    metadata['target_folder'] = folder_name
                    
                    base = item.split('.')[0]
                    if '_to_' in base:
                        parts = base.split('_')
                        try:
                            to_idx = parts.index('to')
                            metadata['target_branch'] = parts[to_idx+1]
                            metadata['product_category'] = parts[to_idx+2]
                        except (ValueError, IndexError):
                            pass
                results.append(metadata)
