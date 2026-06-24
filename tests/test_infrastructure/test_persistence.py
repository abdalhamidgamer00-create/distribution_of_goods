"""Tests for infrastructure.repositories.persistence modules."""

import os
import tempfile
import shutil
from unittest.mock import patch, MagicMock

import pandas as pd
import pytest

from src.domain.models.entities import Product, Branch, StockLevel
from src.domain.models.distribution import (
    Transfer, DistributionResult, ConsolidatedLogisticsReport, LogisticsRecord
)
from src.infrastructure.repositories.persistence.transfers_persistence import (
    save_step7_transfers,
    save_step8_split_transfers,
    _group_transfers_by_pair,
    _group_transfers_by_category,
    _prepare_transfer_dataframe,
    _group_transfers_by_source_and_category,
)
from src.infrastructure.repositories.persistence.surplus_persistence import (
    save_surplus_reports,
    _group_surplus_by_branch_category,
    _persist_category_surplus,
    _persist_total_branch_surplus,
)
from src.infrastructure.repositories.persistence.combined_transfers_persistence import (
    save_step11_combined_transfers,
    _persist_merged_outputs,
    _persist_separate_outputs,
)
from src.infrastructure.repositories.persistence.shortage_persistence import (
    save_shortage_reports,
    _group_shortage_by_category,
    _format_shortage_row,
)


@pytest.fixture
def tmp_dir():
    d = tempfile.mkdtemp()
    yield d
    shutil.rmtree(d, ignore_errors=True)


def _make_transfer(source="admin", target="star", product_name="Product A Tab", qty=5):
    product = Product(code="001", name=product_name)
    return Transfer(
        product=product,
        from_branch=Branch(name=source),
        to_branch=Branch(name=target),
        quantity=qty,
        sender_balance=10.0,
        receiver_balance=3.0,
    )


def _make_distribution_result(
    product_name="Product A Tab", surplus_branch="admin", surplus_qty=5
):
    product = Product(code="001", name=product_name)
    return DistributionResult(
        product=product,
        transfers=[],
        remaining_needed=0,
        remaining_shortage=3,
        remaining_surplus=surplus_qty,
        remaining_branch_surplus={surplus_branch: surplus_qty},
        branch_balances={"administration": 10.0, "star": 5.0},
        total_sales=100.0,
    )


# ==========================================================================
# Transfers Persistence Tests
# ==========================================================================


class TestGroupTransfersByPair:
    def test_groups_correctly(self):
        t1 = _make_transfer("admin", "star")
        t2 = _make_transfer("admin", "shahid")
        t3 = _make_transfer("admin", "star")
        result = _group_transfers_by_pair([t1, t2, t3])
        assert len(result[("admin", "star")]) == 2
        assert len(result[("admin", "shahid")]) == 1


class TestGroupTransfersByCategory:
    def test_groups_by_product_type(self):
        t1 = _make_transfer(product_name="Aspirin Tab")
        t2 = _make_transfer(product_name="Cough Syrup")
        result = _group_transfers_by_category([t1, t2])
        categories = [k[2] for k in result.keys()]
        assert "tablets_and_capsules" in categories
        assert "syrups" in categories


class TestGroupTransfersBySourceAndCategory:
    def test_groups_by_source_and_category(self):
        t1 = _make_transfer(source="admin", product_name="Amoxicillin Cap")
        t2 = _make_transfer(source="admin", product_name="Ibuprofen Syrup")
        t3 = _make_transfer(source="star", product_name="Paracetamol Tab")
        result = _group_transfers_by_source_and_category([t1, t2, t3])
        assert ("admin", "tablets_and_capsules") in result
        assert ("admin", "syrups") in result
        assert ("star", "tablets_and_capsules") in result


class TestPrepareTransferDataframe:
    def test_returns_sorted_dataframe(self):
        transfers = [
            _make_transfer(product_name="Zebra Tab"),
            _make_transfer(product_name="Alpha Cap"),
        ]
        df = _prepare_transfer_dataframe(transfers, "star")
        assert df.iloc[0]['product_name'] == "Alpha Cap"
        assert df.iloc[1]['product_name'] == "Zebra Tab"

    def test_empty_list(self):
        df = _prepare_transfer_dataframe([], "star")
        assert df.empty

    def test_no_target_name_sorts_by_name_and_branch(self):
        t1 = _make_transfer(target="star", product_name="Beta Tab")
        t2 = _make_transfer(target="admin", product_name="Alpha Tab")
        df = _prepare_transfer_dataframe([t1, t2])
        assert df.iloc[0]['product_name'] == "Alpha Tab"


class TestSaveStep7Transfers:
    def test_creates_csv_files(self, tmp_dir):
        transfers = [
            _make_transfer("admin", "star"),
            _make_transfer("admin", "shahid"),
        ]
        save_step7_transfers(transfers, tmp_dir)
        files = []
        for root, _, filenames in os.walk(tmp_dir):
            files.extend(filenames)
        csv_files = [f for f in files if f.endswith('.csv')]
        assert len(csv_files) >= 2

    def test_empty_transfers_returns_early(self, tmp_dir):
        save_step7_transfers([], tmp_dir)
        assert os.listdir(tmp_dir) == []

    @patch('src.infrastructure.repositories.persistence.transfers_persistence.save_formatted_excel')
    def test_with_excel_dir(self, mock_excel, tmp_dir):
        excel_dir = os.path.join(tmp_dir, "excel")
        transfers = [_make_transfer("admin", "star")]
        save_step7_transfers(
            transfers, tmp_dir, excel_dir=excel_dir, timestamp="20240101"
        )
        assert mock_excel.called


class TestSaveStep8SplitTransfers:
    @patch('src.infrastructure.repositories.persistence.transfers_persistence.save_formatted_excel')
    def test_creates_split_files(self, mock_excel, tmp_dir):
        excel_dir = os.path.join(tmp_dir, "excel")
        transfers = [_make_transfer("admin", "star", "Aspirin Tab")]
        save_step8_split_transfers(transfers, tmp_dir, excel_dir, "20240101")
        csv_files = []
        for root, _, filenames in os.walk(tmp_dir):
            csv_files.extend(f for f in filenames if f.endswith('.csv'))
        assert len(csv_files) >= 1
        assert mock_excel.called


# ==========================================================================
# Surplus Persistence Tests
# ==========================================================================


class TestGroupSurplusByBranchCategory:
    def test_groups_correctly(self):
        results = [
            _make_distribution_result("Aspirin Tab", "admin", 5),
            _make_distribution_result("Cough Syrup", "admin", 3),
            _make_distribution_result("Aspirin Tab", "star", 7),
        ]
        grouped = _group_surplus_by_branch_category(results)
        assert "admin" in grouped
        assert "star" in grouped

    def test_skips_zero_surplus(self):
        result = _make_distribution_result("Test Tab", "admin", 0)
        grouped = _group_surplus_by_branch_category([result])
        assert grouped == {}


class TestPersistCategorySurplus:
    def test_creates_csv_and_excel(self, tmp_dir):
        items = [
            {'code': '001', 'product_name': 'Product A', 'remaining_surplus': 5},
        ]
        _persist_category_surplus("admin", "tablets_and_capsules", "20240101", items, tmp_dir)
        csv_dir = os.path.join(tmp_dir, "csv", "admin")
        excel_dir = os.path.join(tmp_dir, "excel", "admin")
        assert os.path.exists(csv_dir)
        assert os.path.exists(excel_dir)
        csv_files = [f for f in os.listdir(csv_dir) if f.endswith('.csv')]
        assert len(csv_files) == 1


class TestPersistTotalBranchSurplus:
    def test_creates_total_files(self, tmp_dir):
        items = [
            {'code': '001', 'product_name': 'Product A', 'remaining_surplus': 5},
            {'code': '002', 'product_name': 'Product B', 'remaining_surplus': 3},
        ]
        os.makedirs(os.path.join(tmp_dir, "csv", "admin"), exist_ok=True)
        os.makedirs(os.path.join(tmp_dir, "excel", "admin"), exist_ok=True)
        _persist_total_branch_surplus("admin", "20240101", items, tmp_dir)
        csv_dir = os.path.join(tmp_dir, "csv", "admin")
        csv_files = [f for f in os.listdir(csv_dir) if 'total' in f]
        assert len(csv_files) == 1


class TestSaveSurplusReports:
    def test_end_to_end(self, tmp_dir):
        results = [_make_distribution_result("Aspirin Tab", "admin", 5)]
        save_surplus_reports(results, tmp_dir)
        csv_dir = os.path.join(tmp_dir, "csv", "admin")
        assert os.path.exists(csv_dir)


# ==========================================================================
# Combined Transfers Persistence Tests
# ==========================================================================


class TestPersistMergedOutputs:
    @patch('src.infrastructure.repositories.persistence.combined_transfers_persistence.save_formatted_excel')
    def test_creates_merged_files(self, mock_excel, tmp_dir):
        branch = Branch(name="admin")
        items = [{
            'category': 'tablets',
            'dataframe': pd.DataFrame({
                'code': ['001'], 'product_name': ['Product A']
            })
        }]
        _persist_merged_outputs(branch, items, "20240101", tmp_dir)
        csv_files = []
        for root, _, filenames in os.walk(tmp_dir):
            csv_files.extend(f for f in filenames if f.endswith('.csv'))
        assert len(csv_files) == 1
        assert mock_excel.called


class TestPersistSeparateOutputs:
    @patch('src.infrastructure.repositories.persistence.combined_transfers_persistence.save_formatted_excel')
    def test_creates_separate_files(self, mock_excel, tmp_dir):
        branch = Branch(name="admin")
        items = [{
            'target': 'star',
            'category': 'tablets',
            'dataframe': pd.DataFrame({
                'code': ['001'], 'product_name': ['Product A']
            })
        }]
        _persist_separate_outputs(branch, items, "20240101", tmp_dir)
        csv_files = []
        for root, _, filenames in os.walk(tmp_dir):
            csv_files.extend(f for f in filenames if f.endswith('.csv'))
        assert len(csv_files) == 1
        assert mock_excel.called


class TestSaveStep11CombinedTransfers:
    @patch('src.infrastructure.repositories.persistence.combined_transfers_persistence.save_formatted_excel')
    def test_end_to_end(self, mock_excel, tmp_dir):
        branch = Branch(name="admin")
        merged = [{
            'category': 'tablets',
            'dataframe': pd.DataFrame({'code': ['001'], 'product_name': ['P A']})
        }]
        separate = [{
            'target': 'star',
            'category': 'tablets',
            'dataframe': pd.DataFrame({'code': ['001'], 'product_name': ['P A']})
        }]
        save_step11_combined_transfers(
            branch, merged, separate, "20240101", tmp_dir
        )
        all_files = []
        for root, _, filenames in os.walk(tmp_dir):
            all_files.extend(filenames)
        assert len(all_files) >= 2


# ==========================================================================
# Shortage Persistence Tests
# ==========================================================================


class TestGroupShortageByCategory:
    def test_groups_by_product_category(self):
        results = [
            _make_distribution_result("Aspirin Tab", "admin", 5),
            _make_distribution_result("Cough Syrup", "admin", 3),
        ]
        grouped = _group_shortage_by_category(results)
        assert "tablets_and_capsules" in grouped
        assert "syrups" in grouped

    def test_skips_zero_shortage(self):
        result = _make_distribution_result("Test Tab", "admin", 5)
        result.remaining_shortage = 0
        grouped = _group_shortage_by_category([result])
        assert grouped == {}


class TestFormatShortageRow:
    def test_includes_required_fields(self):
        result = _make_distribution_result("Aspirin Tab", "admin", 5)
        row = _format_shortage_row(result)
        assert "كود" in row
        assert "إسم الصنف" in row
        assert "كمية النقص" in row
        assert row["كود"] == "001"

    def test_includes_branch_balances(self):
        result = _make_distribution_result("Aspirin Tab", "admin", 5)
        result.branch_balances = {"administration": 10.0, "star": 5.0}
        row = _format_shortage_row(result)
        assert row["رصيد الادارة"] == 10.0


class TestSaveShortageReports:
    def test_end_to_end(self, tmp_dir):
        results = [_make_distribution_result("Aspirin Tab", "admin", 5)]
        save_shortage_reports(results, tmp_dir)
        csv_dir = os.path.join(tmp_dir, "csv")
        assert os.path.exists(csv_dir)
        csv_files = [f for f in os.listdir(csv_dir) if f.endswith('.csv')]
        assert len(csv_files) >= 1
