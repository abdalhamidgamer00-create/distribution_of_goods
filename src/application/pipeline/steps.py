from src.domain.models.step import Step
from src.application.pipeline.workflow import PipelineManager

# Initialize the manager once
manager = PipelineManager()

# Available steps definition, now mapped to Domain Services
AVAILABLE_STEPS = [
    Step(
        id="1",
        name="Data Archiving",
        description="Archive and clear previous output data",
        function=lambda **kwargs: manager.run_service("archive", **kwargs)
    ),
    Step(
        id="2",
        name="Source Ingestion",
        description="Convert raw Excel input to CSV format",
        function=lambda **kwargs: manager.run_service("ingest", **kwargs)
    ),
    Step(
        id="3",
        name="Inventory Validation",
        description="Validate data integrity and business rules",
        function=lambda **kwargs: manager.run_service("validate", **kwargs)
    ),
    Step(
        id="4",
        name="Sales Analytics",
        description="Generate sales intelligence and performance reports",
        function=lambda **kwargs: manager.run_service("analyze", **kwargs)
    ),
    Step(
        id="5",
        name="Schema Normalization",
        description="Standardize column headers and data formats",
        function=lambda **kwargs: manager.run_service("normalize", **kwargs)
    ),
    Step(
        id="6",
        name="Branch Segmentation",
        description="Partition global data into branch-specific datasets",
        function=lambda **kwargs: manager.run_service("segment", **kwargs)
    ),
    Step(
        id="7",
        name="Transfer Optimization",
        description="Calculate optimal stock movements between branches",
        function=lambda **kwargs: manager.run_service("optimize", **kwargs)
    ),
    Step(
        id="8",
        name="Transfer Classification",
        description="Group transfers by category and convert to Excel",
        function=lambda **kwargs: manager.run_service("classify", **kwargs)
    ),
    Step(
        id="9",
        name="Surplus Reporting",
        description="Report excess inventory with no local demand",
        function=lambda **kwargs: manager.run_service("report_surplus", **kwargs)
    ),
    Step(
        id="10",
        name="Shortage Reporting",
        description="Identify and report network-wide inventory gaps",
        function=lambda **kwargs: manager.run_service("report_shortage", **kwargs)
    ),
    Step(
        id="11",
        name="Consolidated Reporting",
        description="Merge transfers and surplus into final logistics files",
        function=lambda **kwargs: manager.run_service("consolidate", **kwargs)
    )
]
