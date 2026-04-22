import sys
from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from src.presentation.gui.services.transfer_ratio_service import (
    compare_transfer_workbooks,
    compare_transfer_workbook_sets,
)


def test_compare_transfer_workbooks_detects_missing_rows(tmp_path):
    expected_path = tmp_path / "expected.xlsx"
    actual_path = tmp_path / "actual.xlsx"

    expected_df = pd.DataFrame(
        [
            {
                "source_branch": "administration",
                "target_branch": "shahid",
                "code": "1001",
                "product_name": "Item A",
                "quantity_to_transfer": 5,
            },
            {
                "source_branch": "administration",
                "target_branch": "okba",
                "code": "1002",
                "product_name": "Item B",
                "quantity_to_transfer": 3,
            },
        ]
    )
    actual_df = pd.DataFrame(
        [
            {
                "source_branch": "administration",
                "target_branch": "shahid",
                "code": "1001",
                "product_name": "Item A",
                "quantity_to_transfer": 5,
            }
        ]
    )

    expected_df.to_excel(expected_path, index=False)
    actual_df.to_excel(actual_path, index=False)

    result = compare_transfer_workbooks(str(expected_path), str(actual_path))

    assert result.overall["expected_items"] == 2
    assert result.overall["matched_items"] == 1
    assert result.overall["item_ratio"] == 50.0
    assert len(result.missing) == 1


def test_compare_transfer_workbooks_uses_quantity_ratio(tmp_path):
    expected_path = tmp_path / "expected_qty.xlsx"
    actual_path = tmp_path / "actual_qty.xlsx"

    expected_df = pd.DataFrame(
        [
            {
                "source_branch": "administration",
                "target_branch": "shahid",
                "code": "1001",
                "product_name": "Item A",
                "quantity_to_transfer": 10,
            }
        ]
    )
    actual_df = pd.DataFrame(
        [
            {
                "source_branch": "administration",
                "target_branch": "shahid",
                "code": "1001",
                "product_name": "Item A",
                "quantity_to_transfer": 4,
            }
        ]
    )

    expected_df.to_excel(expected_path, index=False)
    actual_df.to_excel(actual_path, index=False)

    result = compare_transfer_workbooks(str(expected_path), str(actual_path))

    assert result.overall["item_ratio"] == 100.0
    assert result.overall["quantity_ratio"] == 40.0


def test_compare_transfer_workbooks_can_infer_branch_names_from_filename(tmp_path):
    expected_path = tmp_path / "administration_to_shahid.xlsx"
    actual_path = tmp_path / "transfer_from_administration_to_shahid_final.xlsx"

    expected_df = pd.DataFrame(
        [{"code": "1001", "product_name": "Item A", "quantity_to_transfer": 2}]
    )
    actual_df = pd.DataFrame(
        [{"code": "1001", "product_name": "Item A", "quantity_to_transfer": 2}]
    )

    expected_df.to_excel(expected_path, index=False)
    actual_df.to_excel(actual_path, index=False)

    result = compare_transfer_workbooks(str(expected_path), str(actual_path))

    assert result.overall["item_ratio"] == 100.0
    assert result.by_branch.iloc[0]["source_branch"] == "administration"


def test_compare_transfer_workbooks_supports_code_only_final_file(tmp_path):
    expected_path = tmp_path / "expected_code_only.xlsx"
    actual_path = tmp_path / "testing_output.xlsx"

    expected_df = pd.DataFrame(
        [
            {
                "source_branch": "administration",
                "target_branch": "shahid",
                "code": "48538",
                "product_name": "ROYAL TEA REGIME 25 SACHET",
                "quantity_to_transfer": 1,
            },
            {
                "source_branch": "administration",
                "target_branch": "okba",
                "code": "71851",
                "product_name": "SWEETAL 75 SACHETS",
                "quantity_to_transfer": 1,
            },
        ]
    )
    actual_df = pd.DataFrame(
        [
            {
                "موقع الصنف": ".",
                "رصيد مخزن الإستلام": 0,
                "رصيد مخزن الصرف": 0,
                "كمية": 1,
                "إسم الصنف": "ROYAL TEA REGIME 25 SACHET",
                "كود": "48538",
            },
            {
                "موقع الصنف": ".",
                "رصيد مخزن الإستلام": 2,
                "رصيد مخزن الصرف": 2,
                "كمية": 1,
                "إسم الصنف": "SWEETAL 75 SACHETS",
                "كود": "71851",
            },
        ]
    )

    expected_df.to_excel(expected_path, index=False)
    actual_df.to_excel(actual_path, index=False)

    result = compare_transfer_workbooks(str(expected_path), str(actual_path))

    assert result.overall["item_ratio"] == 100.0
    assert result.matching_basis == "code_only"
    assert result.supports_branch_breakdown is False
    assert result.by_branch.empty


def test_compare_transfer_workbooks_code_only_final_file_tracks_missing_and_quantities(tmp_path):
    expected_path = tmp_path / "expected_code_only_partial.xlsx"
    actual_path = tmp_path / "testing_output_partial.xlsx"

    expected_df = pd.DataFrame(
        [
            {
                "source_branch": "administration",
                "target_branch": "shahid",
                "code": "48538",
                "product_name": "ROYAL TEA REGIME 25 SACHET",
                "quantity_to_transfer": 4,
            },
            {
                "source_branch": "administration",
                "target_branch": "okba",
                "code": "99999",
                "product_name": "MISSING ITEM",
                "quantity_to_transfer": 3,
            },
        ]
    )
    actual_df = pd.DataFrame(
        [
            {
                "كمية": 2,
                "إسم الصنف": "ROYAL TEA REGIME 25 SACHET",
                "كود": "48538",
            }
        ]
    )

    expected_df.to_excel(expected_path, index=False)
    actual_df.to_excel(actual_path, index=False)

    result = compare_transfer_workbooks(str(expected_path), str(actual_path))

    assert result.overall["expected_items"] == 2
    assert result.overall["matched_items"] == 1
    assert result.overall["item_ratio"] == 50.0
    assert result.overall["quantity_ratio"] == round((2 / 7) * 100, 2)
    assert len(result.missing) == 1


def test_compare_transfer_workbook_sets_merges_multiple_files(tmp_path):
    expected_path_1 = tmp_path / "expected_1.xlsx"
    expected_path_2 = tmp_path / "expected_2.xlsx"
    actual_path_1 = tmp_path / "actual_1.xlsx"
    actual_path_2 = tmp_path / "actual_2.xlsx"

    pd.DataFrame(
        [
            {
                "source_branch": "administration",
                "target_branch": "shahid",
                "code": "1001",
                "product_name": "Item A",
                "quantity_to_transfer": 2,
            }
        ]
    ).to_excel(expected_path_1, index=False)

    pd.DataFrame(
        [
            {
                "source_branch": "administration",
                "target_branch": "okba",
                "code": "1002",
                "product_name": "Item B",
                "quantity_to_transfer": 3,
            }
        ]
    ).to_excel(expected_path_2, index=False)

    pd.DataFrame(
        [
            {
                "source_branch": "administration",
                "target_branch": "shahid",
                "code": "1001",
                "product_name": "Item A",
                "quantity_to_transfer": 2,
            }
        ]
    ).to_excel(actual_path_1, index=False)

    pd.DataFrame(
        [
            {
                "source_branch": "administration",
                "target_branch": "okba",
                "code": "1002",
                "product_name": "Item B",
                "quantity_to_transfer": 1,
            }
        ]
    ).to_excel(actual_path_2, index=False)

    result = compare_transfer_workbook_sets(
        [
            (str(expected_path_1), expected_path_1.name),
            (str(expected_path_2), expected_path_2.name),
        ],
        [
            (str(actual_path_1), actual_path_1.name),
            (str(actual_path_2), actual_path_2.name),
        ],
    )

    assert result.overall["expected_items"] == 2
    assert result.overall["matched_items"] == 2
    assert result.overall["item_ratio"] == 100.0
    assert result.overall["quantity_ratio"] == 60.0
