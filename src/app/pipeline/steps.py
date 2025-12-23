from src.core.domain.pipeline.step import Step
from src.app.pipeline.step_1 import step_1_archive_output
from src.app.pipeline.step_2 import step_2_convert_excel_to_csv
from src.app.pipeline.step_3 import step_3_validate_data
from src.app.pipeline.step_4 import step_4_sales_analysis
from src.app.pipeline.step_5 import step_5_rename_columns
from src.app.pipeline.step_6 import step_6_split_by_branches
from src.app.pipeline.step_7 import step_7_generate_transfers
from src.app.pipeline.step_8 import step_8_split_by_product_type
from src.app.pipeline.step_9 import step_9_generate_remaining_surplus
from src.app.pipeline.step_10 import step_10_generate_shortage_files
from src.app.pipeline.step_11 import step_11_generate_combined_transfers


# Available steps definition
AVAILABLE_STEPS = [
    Step(
        id="1",
        name="Archive Previous Output",
        description="Archive previous output files before starting new process (skips if no files exist)",
        function=step_1_archive_output
    ),
    Step(
        id="2",
        name="Convert Excel to CSV",
        description="Convert selected Excel file from input folder to CSV",
        function=step_2_convert_excel_to_csv
    ),
    Step(
        id="3",
        name="Validate Data",
        description="Validate CSV data, check date range (>= 3 months) and Column Headers Validation",
        function=step_3_validate_data
    ),
    Step(
        id="4",
        name="Sales Analysis",
        description="Generate comprehensive sales analysis report with statistics and improvement suggestions",
        function=step_4_sales_analysis
    ),
    Step(
        id="5",
        name="Rename Columns",
        description="Rename CSV columns from Arabic to English",
        function=step_5_rename_columns
    ),
    Step(
        id="6",
        name="Split by Branches",
        description="Split CSV file into 6 separate files, one for each branch",
        function=step_6_split_by_branches
    ),
    Step(
        id="7",
        name="Generate Transfer Files",
        description="Generate transfer CSV files for each branch to all other branches",
        function=step_7_generate_transfers
    ),
    Step(
        id="8",
        name="Split Transfer Files by Product Type & Convert to Excel",
        description="Split transfer files into 6 categories and convert them to Excel format",
        function=step_8_split_by_product_type
    ),
    Step(
        id="9",
        name="Generate Remaining Surplus Files",
        description="Generate files for products with remaining surplus after distribution (CSV and Excel)",
        function=step_9_generate_remaining_surplus
    ),
    Step(
        id="10",
        name="Generate Shortage Files",
        description="Generate files for products where total needed exceeds total surplus (unfulfilled demand)",
        function=step_10_generate_shortage_files
    ),
    Step(
        id="11",
        name="Generate Combined Transfer Files",
        description="Combine transfers with remaining surplus (to admin) in merged/separate formats with balance coloring",
        function=step_11_generate_combined_transfers
    )
]

