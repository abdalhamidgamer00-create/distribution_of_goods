"""Generic use case for generating inventory reports (shortage / surplus)."""

from typing import Callable, List

from src.application.ports.repository import DataRepository
from src.application.use_cases.optimize_transfers import OptimizeTransfers
from src.domain.models.distribution import DistributionResult
from src.shared.utility.logging_utils import get_logger

logger = get_logger(__name__)


class GenerateReport:
    """Calculates distributions and delegates persistence to a callback.

    This replaces the nearly-identical ``ReportShortage`` and
    ``ReportSurplus`` classes by parameterising the save step.
    """

    def __init__(
        self,
        repository: DataRepository,
        save_fn: Callable[[List[DistributionResult]], None],
        report_label: str,
        optimizer: OptimizeTransfers = None,
    ):
        self._repository = repository
        self._save_fn = save_fn
        self._label = report_label
        self._optimizer = optimizer or OptimizeTransfers(repository)

    def execute(self, **kwargs) -> bool:
        config = kwargs.get("config")
        try:
            logger.info("Generating %s reports...", self._label)
            results = self._optimizer.calculate(config)
            self._save_fn(results)
            logger.info("Successfully completed %s reporting", self._label)
            return True
        except Exception as exc:
            logger.exception("%s report generation failed: %s", self._label, exc)
            return False
