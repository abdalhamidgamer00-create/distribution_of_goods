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
        function=lambda use_latest_file=None: manager.run_service("archive")
    ),
    Step(
        id="2",
        name="Source Ingestion",
        description="Convert raw Excel input to CSV format",
        function=lambda use_latest_file=None: manager.run_service(
            "ingest", use_latest_file=use_latest_file
        )
    ),
    Step(
        id="3",
        name="Inventory Validation",
        description="Validate data integrity and business rules",
        function=lambda use_latest_file=None: manager.run_service(
            "validate", use_latest_file=use_latest_file
        )
    ),
    Step(
        id="4",
        name="Sales Analytics",
        description="Generate sales intelligence and performance reports",
        function=lambda use_latest_file=None: manager.run_service(
            "analyze", use_latest_file=use_latest_file
        )
    ),
    Step(
        id="5",
        name="Schema Normalization",
        description="Standardize column headers and data formats",
        function=lambda use_latest_file=None: manager.run_service(
            "normalize", use_latest_file=use_latest_file
        )
    ),
    Step(
        id="6",
        name="Branch Segmentation",
        description="Partition global data into branch-specific datasets",
        function=lambda use_latest_file=None: manager.run_service(
            "segment", use_latest_file=use_latest_file
        )
    ),
    Step(
        id="7",
        name="Transfer Optimization",
        description="Calculate optimal stock movements between branches",
        function=lambda use_latest_file=None: manager.run_service(
            "optimize", use_latest_file=use_latest_file
        )
    ),
    Step(
        id="8",
        name="Transfer Classification",
        description="Group transfers by category and convert to Excel",
        function=lambda use_latest_file=None: manager.run_service(
            "classify", use_latest_file=use_latest_file
        )
    ),
    Step(
        id="9",
        name="Surplus Reporting",
        description="Report excess inventory with no local demand",
        function=lambda use_latest_file=None: manager.run_service(
            "report_surplus", use_latest_file=use_latest_file
        )
    ),
    Step(
        id="10",
        name="Shortage Reporting",
        description="Identify and report network-wide inventory gaps",
        function=lambda use_latest_file=None: manager.run_service(
            "report_shortage", use_latest_file=use_latest_file
        )
    ),
    Step(
        id="11",
        name="Consolidated Reporting",
        description="Merge transfers and surplus into final logistics files",
        function=lambda use_latest_file=None: manager.run_service(
            "consolidate", use_latest_file=use_latest_file
        )
    )
]
