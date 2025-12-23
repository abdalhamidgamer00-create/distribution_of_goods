"""File selection orchestrator."""

from src.app.pipeline.utils.file_selector import finder, interaction


def select_csv_file(
    output_dir: str, csv_files: list, use_latest_file: bool = None
) -> str:
    """Select CSV file based on user choice or use_latest_file flag."""
    if use_latest_file is True:
        return finder.get_latest_csv(output_dir)
    elif use_latest_file is False:
        interaction.show_files_list(csv_files, "CSV")
        return interaction.select_from_list(csv_files)
    else:
        return interaction.select_file_interactive(
            output_dir, csv_files, ['.csv'], "CSV"
        )


def select_excel_file(
    input_dir: str, excel_files: list, use_latest_file: bool = None
) -> str:
    """Select Excel file based on user choice or use_latest_file flag."""
    if use_latest_file is True:
        return finder.get_latest_excel(input_dir)
    elif use_latest_file is False:
        interaction.show_files_list(excel_files, "Excel")
        return interaction.select_from_list(excel_files)
    else:
        return interaction.select_file_interactive(
            input_dir, excel_files, ['.xlsx', '.xls'], "Excel"
        )
