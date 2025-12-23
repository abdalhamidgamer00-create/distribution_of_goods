"""Output file generation writers facade."""

from src.app.pipeline.step_11.combiner.writing import (
    generate_merged_files,
    generate_separate_files
)
from src.app.pipeline.step_11.combiner.writing.utils import get_timestamp

__all__ = ['generate_merged_files', 'generate_separate_files', 'get_timestamp']
