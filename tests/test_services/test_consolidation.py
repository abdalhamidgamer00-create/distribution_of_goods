import pytest
from src.domain.models.entities import Branch, Product, SurplusEntry, NetworkStockState
from src.domain.services.consolidation_service import ConsolidationEngine

def test_consolidation_engine_skips_administration_surplus():
    """Verify that administration does not send surplus to itself."""
    engine = ConsolidationEngine()
    admin_branch = Branch(name='administration')
    product = Product(code='123', name='Test Product')
    surplus_entries = [
        SurplusEntry(product=product, quantity=10, branch=admin_branch)
    ]
    
    network_state = NetworkStockState(balances={
        'administration': {'123': 10.0}
    })

    report = engine.combine_data(
        branch=admin_branch,
        transfers=[],
        surplus_entries=surplus_entries,
        network_state=network_state
    )
    
    # Should have 0 records because surplus is skipped for admin
    assert len(report.records) == 0

def test_consolidation_engine_includes_other_branch_surplus():
    """Verify that other branches DO send surplus to administration."""
    engine = ConsolidationEngine()
    other_branch = Branch(name='asherin')
    product = Product(code='123', name='Test Product')
    surplus_entries = [
        SurplusEntry(product=product, quantity=10, branch=other_branch)
    ]
    
    network_state = NetworkStockState(balances={
        'asherin': {'123': 10.0},
        'administration': {'123': 5.0}
    })

    report = engine.combine_data(
        branch=other_branch,
        transfers=[],
        surplus_entries=surplus_entries,
        network_state=network_state
    )
    
    # Should have 1 record
    assert len(report.records) == 1
    assert report.records[0].target_branch == 'administration'
    assert report.records[0].transfer_type == 'surplus'
    assert report.records[0].sender_balance == 10.0
    assert report.records[0].receiver_balance == 5.0
