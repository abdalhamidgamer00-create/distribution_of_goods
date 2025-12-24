"""Test script for distribution logic"""

import pandas as pd
import random
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.domain.services.branches.config import get_branches
from src.domain.services.calculations.quantity_calculator import calculate_basic_quantities
from src.domain.services.calculations.allocation_calculator import (
    calculate_proportional_allocations_vectorized,
)
from src.domain.services.calculations.order_calculator import (
    get_needing_branches_ordered_by_priority,
    get_surplus_sources_ordered_for_product,
)
from src.domain.models.entities import StockLevel


from src.domain.services.validation import extract_dates_from_header


def load_test_data(csv_path: str):
    """Load and prepare test data"""
    with open(csv_path, 'r', encoding='utf-8-sig') as f:
        first_line = f.readline().strip()
    
    start_date, end_date = extract_dates_from_header(first_line)
    if start_date and end_date:
        df = pd.read_csv(csv_path, skiprows=1, encoding='utf-8-sig')
    else:
        df = pd.read_csv(csv_path, encoding='utf-8-sig')
    branches = get_branches()
    base_columns = ['code', 'product_name', 'selling_price', 'company', 'unit', 
                    'total_sales', 'total_product_balance']
    
    branch_data = {}
    for branch in branches:
        branch_columns = [f'{branch}_sales', f'{branch}_avg_sales', f'{branch}_balance']
        selected_columns = base_columns + branch_columns
        
        branch_df = df[selected_columns].copy()
        branch_df.columns = base_columns + ['sales', 'avg_sales', 'balance']
        branch_df = calculate_basic_quantities(branch_df)
        branch_data[branch] = branch_df
    
    return branch_data, df[base_columns]


def select_diverse_products(branch_data: dict, num_products: int = 20):
    """Select diverse products based on quantity variations"""
    branches = get_branches()
    num_total = len(branch_data[branches[0]])
    
    products_by_category = {
        'proportional': [],  # surplus < needed
        'sufficient': [],     # surplus >= needed, both > 0
        'only_needed': [],    # only needed, no surplus
        'only_surplus': [],   # only surplus, no needed
        'mixed': []           # other cases
    }
    
    for idx in range(num_total):
        total_needed = sum(branch_data[branch].iloc[idx]['needed_quantity'] for branch in branches)
        total_surplus = sum(branch_data[branch].iloc[idx]['surplus_quantity'] for branch in branches)
        num_needing = sum(1 for branch in branches if branch_data[branch].iloc[idx]['needed_quantity'] > 0)
        num_surplus = sum(1 for branch in branches if branch_data[branch].iloc[idx]['surplus_quantity'] > 0)
        
        if total_needed > 0 and total_surplus > 0:
            if total_surplus < total_needed:
                products_by_category['proportional'].append((idx, total_needed, total_surplus))
            else:
                products_by_category['sufficient'].append((idx, total_needed, total_surplus))
        elif total_needed > 0:
            products_by_category['only_needed'].append((idx, total_needed, total_surplus))
        elif total_surplus > 0:
            products_by_category['only_surplus'].append((idx, total_needed, total_surplus))
        else:
            products_by_category['mixed'].append((idx, total_needed, total_surplus))
    
    selected = []
    
    # Prioritize proportional cases (8 products)
    products_by_category['proportional'].sort(key=lambda x: abs(x[1] - x[2]))
    selected.extend([p[0] for p in products_by_category['proportional'][:8]])
    
    # Add sufficient cases (5 products)
    products_by_category['sufficient'].sort(key=lambda x: -x[1])
    selected.extend([p[0] for p in products_by_category['sufficient'][:5]])
    
    # Add only_needed cases (3 products)
    products_by_category['only_needed'].sort(key=lambda x: -x[1])
    selected.extend([p[0] for p in products_by_category['only_needed'][:3]])
    
    # Add only_surplus cases (2 products)
    products_by_category['only_surplus'].sort(key=lambda x: -x[2])
    selected.extend([p[0] for p in products_by_category['only_surplus'][:2]])
    
    # Fill remaining with mixed (2 products)
    random.shuffle(products_by_category['mixed'])
    selected.extend([p[0] for p in products_by_category['mixed'][:2]])
    
    # If still not enough, add more from any category
    if len(selected) < num_products:
        all_remaining = []
        for category in products_by_category.values():
            for p in category:
                if p[0] not in selected:
                    all_remaining.append(p[0])
        random.shuffle(all_remaining)
        selected.extend(all_remaining[:num_products - len(selected)])
    
    return selected[:num_products]


def analyze_product(product_idx: int, branch_data: dict, product_info: pd.DataFrame):
    """Analyze a single product"""
    branches = get_branches()
    
    analysis = {
        'product_idx': product_idx,
        'code': product_info.iloc[product_idx]['code'],
        'product_name': product_info.iloc[product_idx]['product_name'],
        'needing_branches': [],
        'surplus_branches': [],
        'total_needed': 0.0,
        'total_surplus': 0.0,
        'proportional_allocation': {},
        'distribution_details': []
    }
    
    for branch in branches:
        needed = branch_data[branch].iloc[product_idx]['needed_quantity']
        surplus = branch_data[branch].iloc[product_idx]['surplus_quantity']
        avg_sales = branch_data[branch].iloc[product_idx]['avg_sales']
        balance = branch_data[branch].iloc[product_idx]['balance']
        coverage_qty = branch_data[branch].iloc[product_idx]['coverage_quantity']
        
        if needed > 0:
            analysis['needing_branches'].append({
                'branch': branch,
                'needed': needed,
                'avg_sales': avg_sales,
                'balance': balance,
                'coverage_quantity': coverage_qty
            })
            analysis['total_needed'] += needed
        
        if surplus > 0:
            analysis['surplus_branches'].append({
                'branch': branch,
                'surplus': surplus,
                'avg_sales': avg_sales,
                'balance': balance
            })
            analysis['total_surplus'] += surplus
    
    analysis['needing_branches'].sort(key=lambda x: (-x['avg_sales'], x['balance']))
    analysis['surplus_branches'].sort(key=lambda x: (-x['avg_sales'], x['balance']))
    
    if analysis['total_needed'] > 0 and analysis['total_surplus'] > 0:
            # استخدام الدالة الجديدة vectorized للحصول على التوزيع النسبي
            all_allocations = calculate_proportional_allocations_vectorized(branch_data, branches)
            allocation = all_allocations.get(product_idx, {})
            analysis['proportional_allocation'] = allocation
            
            if analysis['total_surplus'] < analysis['total_needed']:
                surplus_available = {}
                for sb in analysis['surplus_branches']:
                    surplus_available[sb['branch']] = sb['surplus']
                
                for needing_branch in analysis['needing_branches']:
                    branch_name = needing_branch['branch']
                    needed = needing_branch['needed']
                    allocated = allocation.get(branch_name, needed)
                    proportion = (needed / analysis['total_needed']) * 100 if analysis['total_needed'] > 0 else 0
                    allocated_proportion = (allocated / analysis['total_surplus']) * 100 if analysis['total_surplus'] > 0 else 0
                    
                    # Create StockLevel objects for all branches
                    branch_stocks = {}
                    for b_name in branches:
                        row = branch_data[b_name].iloc[product_idx]
                        branch_stocks[b_name] = StockLevel(
                            needed=int(row['needed_quantity']),
                            surplus=int(row['surplus_quantity']),
                            balance=float(row['balance']),
                            avg_sales=float(row['avg_sales'])
                        )
                    
                    needing_order = get_needing_branches_ordered_by_priority(branch_stocks)
                    # الحصول على قائمة الفروع التي لديها فائض
                    surplus_branches = [sb['branch'] for sb in analysis['surplus_branches']]
                    # ترتيب الفروع التي لديها فائض حسب ترتيب needing_order (الأولوية للفروع التي تحتاج أكثر)
                    search_order = [b for b in needing_order if b in surplus_branches]
                    # إضافة باقي الفروع التي لديها فائض ولكنها ليست في needing_order
                    search_order.extend([b for b in surplus_branches if b not in search_order])
                    
                    distribution = {
                        'needing_branch': branch_name,
                        'needed_amount': needed,
                        'allocated_amount': allocated,
                        'proportion_of_needed': round(proportion, 2),
                        'proportion_of_surplus': round(allocated_proportion, 2),
                        'sources': []
                    }
                    
                    remaining = allocated
                    for source_branch in search_order:
                        if remaining <= 0:
                            break
                        available = surplus_available.get(source_branch, 0.0)
                        if available > 0 and source_branch != branch_name:
                            amount_from_source = round(min(remaining, available), 2)
                            distribution['sources'].append({
                                'source_branch': source_branch,
                                'amount': amount_from_source,
                                'available_surplus': round(available, 2)
                            })
                            surplus_available[source_branch] = round(available - amount_from_source, 2)
                            remaining = round(remaining - amount_from_source, 2)
                    
                    analysis['distribution_details'].append(distribution)
    
    return analysis


def generate_report(analyses: list):
    """Generate detailed report"""
    report_lines = []
    report_lines.append("=" * 100)
    report_lines.append("DISTRIBUTION LOGIC TEST REPORT")
    report_lines.append("=" * 100)
    report_lines.append(f"\nTotal Products Tested: {len(analyses)}")
    report_lines.append("\n" + "=" * 100)
    
    for i, analysis in enumerate(analyses, 1):
        report_lines.append(f"\n{'='*100}")
        report_lines.append(f"PRODUCT {i}: {analysis['code']} - {analysis['product_name']}")
        report_lines.append(f"{'='*100}")
        
        report_lines.append(f"\n[SUMMARY]")
        report_lines.append(f"  Total Needed: {analysis['total_needed']:.2f}")
        report_lines.append(f"  Total Surplus: {analysis['total_surplus']:.2f}")
        report_lines.append(f"  Coverage: {(analysis['total_surplus'] / analysis['total_needed'] * 100) if analysis['total_needed'] > 0 else 0:.2f}%")
        
        report_lines.append(f"\n[NEEDING BRANCHES] ({len(analysis['needing_branches'])})")
        for nb in analysis['needing_branches']:
            report_lines.append(f"  - {nb['branch']:10s}: Needed={nb['needed']:8.2f}, Avg_Sales={nb['avg_sales']:6.2f}, Balance={nb['balance']:8.2f}, Coverage={nb['coverage_quantity']:8.2f}")
        
        report_lines.append(f"\n[SURPLUS BRANCHES] ({len(analysis['surplus_branches'])})")
        for sb in analysis['surplus_branches']:
            report_lines.append(f"  - {sb['branch']:10s}: Surplus={sb['surplus']:8.2f}, Avg_Sales={sb['avg_sales']:6.2f}, Balance={sb['balance']:8.2f}")
        
        if analysis['total_surplus'] < analysis['total_needed']:
            report_lines.append(f"\n[PROPORTIONAL ALLOCATION] (Surplus < Needed)")
            for branch_name, allocated in analysis['proportional_allocation'].items():
                needed = next(nb['needed'] for nb in analysis['needing_branches'] if nb['branch'] == branch_name)
                proportion = (needed / analysis['total_needed']) * 100
                allocated_pct = (allocated / analysis['total_surplus']) * 100
                report_lines.append(f"  - {branch_name:10s}: Needed={needed:8.2f} ({proportion:5.2f}%), Allocated={allocated:8.2f} ({allocated_pct:5.2f}%)")
        
        if analysis['distribution_details']:
            report_lines.append(f"\n[DISTRIBUTION DETAILS]")
            for dist in analysis['distribution_details']:
                report_lines.append(f"\n  Branch: {dist['needing_branch']}")
                report_lines.append(f"    Needed: {dist['needed_amount']:.2f}")
                report_lines.append(f"    Allocated: {dist['allocated_amount']:.2f} ({dist['proportion_of_needed']:.2f}% of needed, {dist['proportion_of_surplus']:.2f}% of surplus)")
                if dist['sources']:
                    report_lines.append(f"    Sources:")
                    for source in dist['sources']:
                        report_lines.append(f"      - {source['source_branch']:10s}: {source['amount']:.2f} from {source['available_surplus']:.2f} available")
                else:
                    report_lines.append(f"    Sources: None (no surplus available)")
        
        report_lines.append("")
    
    report_lines.append("=" * 100)
    report_lines.append("END OF REPORT")
    report_lines.append("=" * 100)
    
    return "\n".join(report_lines)


def main():
    """Main test function"""
    import os
    import sys
    
    try:
        from src.shared.utility.file_handler import (
            get_csv_files,
            get_latest_file,
            get_file_path,
        )
    except ImportError as e:
        print(f"Error importing modules: {e}")
        print("Please make sure you're running from the project root directory")
        sys.exit(1)
    
    renamed_dir = "data/output/renamed"
    csv_files = get_csv_files(renamed_dir)
    
    if not csv_files:
        print(f"No CSV files found in {renamed_dir}")
        print("Please run step 4 (Rename Columns) first to generate renamed CSV files")
        return
    
    csv_file = get_latest_file(renamed_dir, '.csv')
    if not csv_file:
        csv_file = csv_files[0]
    
    csv_path = get_file_path(csv_file, renamed_dir)
    print(f"Loading data from: {csv_file}")
    
    branch_data, product_info = load_test_data(csv_path)
    selected_products = select_diverse_products(branch_data, 20)
    
    print(f"\nSelected {len(selected_products)} products for testing")
    print(f"Product indices: {selected_products[:10]}...")
    
    analyses = []
    for product_idx in selected_products:
        analysis = analyze_product(product_idx, branch_data, product_info)
        analyses.append(analysis)
    
    report = generate_report(analyses)
    
    output_file = "test_distribution_report.txt"
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(report)
    
    print(f"\nReport saved to: {output_file}")
    print("\n" + "="*100)
    print("REPORT SUMMARY")
    print("="*100)
    print(report[:2000])
    print("\n... (full report saved to file)")


if __name__ == "__main__":
    main()

