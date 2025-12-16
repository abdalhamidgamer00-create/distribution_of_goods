#!/usr/bin/env python3
"""
Find problematic rows in CSV files that cause TypeError
Usage: python find_problematic_rows.py <csv_file_path>
"""

import sys
import csv

def find_problematic_balance_values(csv_path):
    """Find non-numeric values in balance columns"""
    
    print(f"🔍 Analyzing file: {csv_path}\n")
    print("="*80)
    
    with open(csv_path, 'r', encoding='utf-8-sig') as f:
        reader = csv.reader(f)
        headers = next(reader)
        
        # Find balance column indices
        balance_cols = {}
        for idx, header in enumerate(headers):
            if 'balance' in header.lower():
                balance_cols[idx] = header
        
        print(f"\n📊 Found {len(balance_cols)} balance columns:")
        for idx, name in balance_cols.items():
            print(f"   Column {idx}: {name}")
        print("\n" + "="*80)
        
        # Check each row
        problematic_rows = []
        
        for line_num, row in enumerate(reader, start=2):  # start=2 because line 1 is header
            for col_idx, col_name in balance_cols.items():
                if col_idx < len(row):
                    value = row[col_idx]
                    
                    # Try to convert to float
                    if value.strip():  # Not empty
                        try:
                            float(value)
                        except ValueError:
                            # Non-numeric value found!
                            code = row[0] if len(row) > 0 else 'N/A'
                            product = row[1] if len(row) > 1 else 'N/A'
                            
                            problematic_rows.append({
                                'line': line_num,
                                'column': col_name,
                                'column_idx': col_idx,
                                'code': code,
                                'product': product,
                                'value': value
                            })
                            
                            print(f"\n❌ Line {line_num}:")
                            print(f"   Code: {code}")
                            print(f"   Product: {product[:50]}...")  # First 50 chars
                            print(f"   Column: {col_name} (index {col_idx})")
                            print(f"   Problematic value: '{value}'")
        
        print("\n" + "="*80)
        print(f"\n📌 Total problematic rows: {len(problematic_rows)}")
        
        if problematic_rows:
            print("\n🎯 Summary of first 10 issues:")
            for item in problematic_rows[:10]:
                print(f"   Line {item['line']}: {item['column']} = '{item['value']}'")
            
            if len(problematic_rows) > 10:
                print(f"\n   ... and {len(problematic_rows) - 10} more")
        else:
            print("\n✅ All balance values are numeric!")
        
        return problematic_rows

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python find_problematic_rows.py <csv_file_path>")
        print("\nExample:")
        print("  python find_problematic_rows.py data/output/converted/renamed/file.csv")
        sys.exit(1)
    
    csv_path = sys.argv[1]
    
    try:
        problematic_rows = find_problematic_balance_values(csv_path)
        
        # Exit with code 1 if problems found
        sys.exit(1 if problematic_rows else 0)
        
    except FileNotFoundError:
        print(f"❌ Error: File not found: {csv_path}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
