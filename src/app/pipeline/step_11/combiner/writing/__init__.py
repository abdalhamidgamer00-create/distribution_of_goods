"""Writing Package."""

from src.app.pipeline.step_11.combiner.writing.merged import (
    generate_merged_files
)
from src.app.pipeline.step_11.combiner.writing.separate import (
    generate_separate_files
)

__all__ = ['generate_merged_files', 'generate_separate_files']
