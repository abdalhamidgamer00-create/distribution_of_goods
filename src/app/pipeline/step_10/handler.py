"""Step 10: Generate shortage files handler

Generates files for products where total needed exceeds total surplus.
"""

import os
from datetime import datetime
import pandas as pd
from src.core.domain.branches.config import get_branches
from src.core.domain.classification.product_classifier import (
    classify_product_type,
    get_product_categories,
)
from src.shared.utils.logging_utils import get_logger
from src.app.pipeline.step_10.shortage_calculator import calculate_shortage_products

logger = get_logger(__name__)

# Output directories
ANALYTICS_DIR = os.path.join("data", "output", "branches", "analytics")
CSV_OUTPUT_DIR = os.path.join("data", "output", "shortage", "csv")
EXCEL_OUTPUT_DIR = os.path.join("data", "output", "shortage", "excel")


def step_10_generate_shortage_files(use_latest_file: bool = None) -> bool:
    """
    Step 10: Generate shortage files.
    
    Creates CSV and Excel files containing products where total needed
    quantity across all branches exceeds total surplus.
    
    Args:
        use_latest_file: Not used, kept for consistency with other handlers
        
    Returns:
        True if successful, False otherwise
    """
    branches = get_branches()
    
    # Validate analytics directories exist
    for branch in branches:
        branch_dir = os.path.join(ANALYTICS_DIR, branch)
        if not os.path.exists(branch_dir):
            logger.error("Analytics directory not found: %s", branch_dir)
            logger.error("Please run step 6 (Split by Branches) first")
            return False
    
    try:
        logger.info("Calculating shortage products...")
        logger.info("-" * 50)
        
        # Calculate shortage products
        shortage_df, has_date_header, first_line = calculate_shortage_products(ANALYTICS_DIR)
        
        if shortage_df.empty:
            logger.info("No shortage products found. All needs are covered by surplus!")
            return True
        
        logger.info("Found %d products with shortage", len(shortage_df))
        
        # Add product type for categorization
        shortage_df['product_type'] = shortage_df['product_name'].apply(classify_product_type)
        
        # Create output directories
        os.makedirs(CSV_OUTPUT_DIR, exist_ok=True)
        os.makedirs(EXCEL_OUTPUT_DIR, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        base_name = "shortage_products"
        
        # Generate files split by category
        categories = get_product_categories()
        generated_files = {}
        
        for category in categories:
            category_df = shortage_df[shortage_df['product_type'] == category].copy()
            
            if len(category_df) == 0:
                continue
            
            # Sort by shortage_quantity (descending)
            category_df = category_df.sort_values(
                'shortage_quantity',
                ascending=False
            )
            
            # Remove product_type column
            category_df = category_df.drop('product_type', axis=1)
            
            # Generate CSV file
            csv_filename = f"{base_name}_{timestamp}_{category}.csv"
            csv_path = os.path.join(CSV_OUTPUT_DIR, csv_filename)
            
            with open(csv_path, 'w', encoding='utf-8-sig', newline='') as f:
                if has_date_header:
                    f.write(first_line + '\n')
                category_df.to_csv(f, index=False, lineterminator='\n')
            
            generated_files[category] = {
                'csv_path': csv_path,
                'df': category_df,
                'count': len(category_df)
            }
        
        # Also generate a combined file (all categories)
        all_df = shortage_df.drop('product_type', axis=1).copy()
        all_csv_filename = f"{base_name}_{timestamp}_all.csv"
        all_csv_path = os.path.join(CSV_OUTPUT_DIR, all_csv_filename)
        
        with open(all_csv_path, 'w', encoding='utf-8-sig', newline='') as f:
            if has_date_header:
                f.write(first_line + '\n')
            all_df.to_csv(f, index=False, lineterminator='\n')
        
        generated_files['all'] = {
            'csv_path': all_csv_path,
            'df': all_df,
            'count': len(all_df)
        }
        
        # Convert to Excel
        logger.info("Converting to Excel format...")
        
        for category, file_info in generated_files.items():
            excel_filename = os.path.splitext(os.path.basename(file_info['csv_path']))[0] + '.xlsx'
            excel_path = os.path.join(EXCEL_OUTPUT_DIR, excel_filename)
            
            try:
                with pd.ExcelWriter(excel_path, engine='openpyxl') as writer:
                    file_info['df'].to_excel(writer, index=False, sheet_name='Shortage Products')
            except Exception as e:
                logger.error("Error creating Excel file for %s: %s", category, e)
        
        # Log summary
        logger.info("=" * 50)
        logger.info("Generated shortage files:")
        
        for category in categories:
            if category in generated_files:
                logger.info("  - %s: %d products", category, generated_files[category]['count'])
        
        logger.info("  - all (combined): %d products", generated_files['all']['count'])
        logger.info("")
        logger.info("Total shortage quantity: %d units", shortage_df['shortage_quantity'].sum())
        logger.info("")
        logger.info("CSV files saved to: %s", CSV_OUTPUT_DIR)
        logger.info("Excel files saved to: %s", EXCEL_OUTPUT_DIR)
        
        return True
        
    except Exception as e:
        logger.exception("Error generating shortage files: %s", e)
        return False

