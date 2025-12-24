"""Specialized component for mapping and listing output artifacts."""

import os
from typing import List, Dict, Optional
from src.infrastructure.repositories.metadata.output_manager import list_artifacts


class ArtifactLister:
    """Handles discovery and categorization of output files."""

    def __init__(self, output_directory: str, **kwargs):
        self._output_directory = output_directory
        self._surplus_directory = kwargs.get('surplus_dir', output_directory)
        self._shortage_directory = kwargs.get('shortage_dir', output_directory)

    def list_outputs(
        self, 
        category_name: str, 
        branch_filter: Optional[str] = None
    ) -> List[Dict]:
        """Lists available output artifacts for a specific category."""
        mapping = self._get_category_mapping()
        if category_name not in mapping:
            return []
            
        config = mapping[category_name]
        return list_artifacts(
            category_name, 
            config['base_directory'], 
            config['search_patterns'],
            branch_filter
        )

    def _get_category_mapping(self) -> Dict:
        """Returns internal configuration for listing artifacts."""
        return {
            'transfers': {
                'base_directory': self._output_directory,
                'search_patterns': {
                    'csv': 'transfers_from_', 
                    'excel': 'transfers_excel_from_'
                }
            },
            'surplus': {
                'base_directory': self._surplus_directory,
                'search_patterns': {'csv': '', 'excel': ''}
            },
            'shortage': {
                'base_directory': self._shortage_directory,
                'search_patterns': {'csv': '', 'excel': ''}
            },
            'merged': {
                'base_directory': "data/output/combined_transfers/merged",
                'search_patterns': {
                    'csv': 'combined_transfers_from_', 
                    'excel': 'combined_transfers_from_'
                }
            },
            'separate': {
                'base_directory': "data/output/combined_transfers/separate",
                'search_patterns': {
                    'csv': 'transfers_from_', 
                    'excel': 'transfers_from_'
                }
            }
        }
