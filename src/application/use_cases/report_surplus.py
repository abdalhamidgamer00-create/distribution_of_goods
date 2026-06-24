"""Use case for reporting products with remaining surplus stock."""

from src.application.ports.repository import DataRepository
from src.application.use_cases.generate_report import GenerateReport
from src.application.use_cases.optimize_transfers import OptimizeTransfers


class ReportSurplus(GenerateReport):
    """Thin wrapper that binds the generic report to surplus persistence."""

    def __init__(
        self,
        repository: DataRepository,
        optimizer: OptimizeTransfers = None,
    ):
        super().__init__(
            repository=repository,
            save_fn=repository.save_remaining_surplus,
            report_label="surplus",
            optimizer=optimizer,
        )
