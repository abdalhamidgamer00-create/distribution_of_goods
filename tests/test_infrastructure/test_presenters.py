"""Tests for infrastructure.repositories.mappers.presenters module."""

import pytest

from src.domain.models.entities import Product, Branch
from src.domain.models.distribution import (
    LogisticsRecord, ConsolidatedLogisticsReport,
)
from src.infrastructure.repositories.mappers.presenters import LogisticsPresenter


def _make_record(product_name="Product A Tab", target="star", category="tablets_and_capsules"):
    product = Product(code="001", name=product_name)
    return LogisticsRecord(
        product=product,
        quantity=10,
        target_branch=target,
        transfer_type="normal",
        sender_balance=20.0,
        receiver_balance=5.0,
        category=category,
    )


def _make_report(records=None):
    if records is None:
        records = [_make_record()]
    return ConsolidatedLogisticsReport(
        source_branch=Branch(name="admin"),
        records=records,
    )


class TestLogisticsPresenter:
    def test_empty_report_returns_empty_lists(self):
        presenter = LogisticsPresenter()
        report = _make_report(records=[])
        merged, separate = presenter.prepare_payloads(report)
        assert merged == []
        assert separate == []

    def test_single_record_produces_merged_payload(self):
        presenter = LogisticsPresenter()
        report = _make_report()
        merged, separate = presenter.prepare_payloads(report)
        assert len(merged) == 1
        assert merged[0]['category'] == 'tablets_and_capsules'
        assert len(merged[0]['dataframe']) == 1

    def test_single_record_produces_separate_payload(self):
        presenter = LogisticsPresenter()
        report = _make_report()
        merged, separate = presenter.prepare_payloads(report)
        assert len(separate) == 1
        assert separate[0]['target'] == 'star'
        assert separate[0]['category'] == 'tablets_and_capsules'

    def test_multiple_categories_merged(self):
        records = [
            _make_record("Tab Product", "star", "tablets_and_capsules"),
            _make_record("Syrup Product", "star", "syrups"),
        ]
        presenter = LogisticsPresenter()
        report = _make_report(records)
        merged, _ = presenter.prepare_payloads(report)
        assert len(merged) == 2

    def test_multiple_targets_separate(self):
        records = [
            _make_record("Tab Product", "star", "tablets_and_capsules"),
            _make_record("Tab Product 2", "shahid", "tablets_and_capsules"),
        ]
        presenter = LogisticsPresenter()
        report = _make_report(records)
        _, separate = presenter.prepare_payloads(report)
        assert len(separate) == 2

    def test_standardize_df_sorts_by_product_name(self):
        records = [
            _make_record("Zebra Product", "star", "tablets_and_capsules"),
            _make_record("Alpha Product", "star", "tablets_and_capsules"),
        ]
        presenter = LogisticsPresenter()
        report = _make_report(records)
        merged, _ = presenter.prepare_payloads(report)
        df = merged[0]['dataframe']
        assert df.iloc[0]['product_name'] == "Alpha Product"
        assert df.iloc[1]['product_name'] == "Zebra Product"

    def test_standardize_df_has_correct_columns(self):
        presenter = LogisticsPresenter()
        report = _make_report()
        merged, _ = presenter.prepare_payloads(report)
        df = merged[0]['dataframe']
        expected = [
            'code', 'product_name', 'quantity_to_transfer',
            'target_branch', 'transfer_type',
            'sender_balance', 'receiver_balance'
        ]
        assert list(df.columns) == expected

    def test_record_with_none_category_defaults_to_other(self):
        record = _make_record(category=None)
        presenter = LogisticsPresenter()
        report = _make_report([record])
        merged, _ = presenter.prepare_payloads(report)
        assert merged[0]['category'] == 'other'
