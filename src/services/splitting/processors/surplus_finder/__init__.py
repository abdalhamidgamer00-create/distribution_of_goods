"""Surplus Finder Package Facade."""

from src.services.splitting.processors.surplus_finder.orchestrator import (
    find_surplus_sources_for_single_product,
)

__all__ = ['find_surplus_sources_for_single_product']
