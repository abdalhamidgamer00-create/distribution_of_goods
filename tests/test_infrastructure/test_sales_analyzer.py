"""Tests for infrastructure.services.analysis.sales_analyzer module."""

import os
import tempfile
import shutil

import pytest

from src.infrastructure.services.analysis.sales_analyzer import (
    analyze_csv_data,
    _read_csv_with_header,
    _build_date_range,
    _calculate_empty_percentage,
    _calculate_cell_stats,
)


@pytest.fixture
def tmp_dir():
    d = tempfile.mkdtemp()
    yield d
    shutil.rmtree(d, ignore_errors=True)


def _create_csv(tmp_dir, content, filename="test.csv"):
    path = os.path.join(tmp_dir, filename)
    with open(path, 'w', encoding='utf-8-sig') as f:
        f.write(content)
    return path


class TestBuildDateRange:
    def test_valid_dates(self):
        from datetime import datetime
        start = datetime(2024, 1, 1)
        end = datetime(2024, 6, 30)
        result = _build_date_range(start, end)
        assert result is not None
        assert result['start'] == "01/01/2024 00:00"
        assert result['end'] == "30/06/2024 00:00"

    def test_none_dates(self):
        result = _build_date_range(None, None)
        assert result is None

    def test_partial_none(self):
        from datetime import datetime
        result = _build_date_range(datetime(2024, 1, 1), None)
        assert result is None


class TestCalculateEmptyPercentage:
    def test_normal_case(self):
        result = _calculate_empty_percentage(50, 1000)
        assert result == 5.0

    def test_zero_total(self):
        result = _calculate_empty_percentage(0, 0)
        assert result == 0.0

    def test_all_empty(self):
        result = _calculate_empty_percentage(100, 100)
        assert result == 100.0


class TestCalculateCellStats:
    def test_returns_correct_stats(self):
        import pandas as pd
        df = pd.DataFrame({
            'a': [1, 2, None],
            'b': [4, None, 6],
        })
        stats = _calculate_cell_stats(df)
        assert stats['total_rows'] == 3
        assert stats['total_columns'] == 2
        assert stats['total_cells'] == 6
        assert stats['empty_cells'] == 2
        assert stats['filled_cells'] == 4
        assert stats['empty_cells_percentage'] == 33.33


class TestReadCsvWithHeader:
    def test_with_date_header(self, tmp_dir):
        content = "من: 01/09/2024 00:00 إلى: 01/12/2024 00:00\ncode,name\n001,A\n002,B"
        path = _create_csv(tmp_dir, content)
        df, date_range = _read_csv_with_header(path)
        assert date_range is not None
        assert len(df) == 2

    def test_without_date_header(self, tmp_dir):
        content = "code,name\n001,A\n002,B"
        path = _create_csv(tmp_dir, content)
        df, date_range = _read_csv_with_header(path)
        assert date_range is None
        assert len(df) == 2


class TestAnalyzeCsvData:
    def test_full_analysis(self, tmp_dir):
        content = "من: 01/09/2024 00:00 إلى: 01/12/2024 00:00\ncode,name,value\n001,A,10\n002,B,20"
        path = _create_csv(tmp_dir, content)
        result = analyze_csv_data(path)
        assert result['total_rows'] == 2
        assert result['total_columns'] == 3
        assert result['date_range'] is not None

    def test_invalid_path_raises(self):
        with pytest.raises(ValueError, match="Error analyzing CSV"):
            analyze_csv_data("/nonexistent/file.csv")
