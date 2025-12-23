"""Header checking logic."""

def check_all_headers(
    actual_headers: list, required_headers: list, optional_headers: list
) -> tuple:
    """Check all headers and return errors and warnings."""
    errors, warnings = [], []
    _add_missing_error(errors, actual_headers, required_headers)
    _add_unknown_warning(
        warnings, actual_headers, required_headers, optional_headers
    )
    
    opt_warn = _check_optional_present(actual_headers, optional_headers)
    if opt_warn:
        warnings.append(opt_warn)
    
    return errors, warnings


def _check_missing_required(
    actual_headers: list, required_headers: list
) -> list:
    """Check for missing required columns."""
    return [
        required for required in required_headers 
        if required not in actual_headers
    ]


def _check_unknown_columns(
    actual_headers: list, required_headers: list, optional_headers: list
) -> list:
    """Check for unknown columns not in required or optional."""
    all_known = required_headers + optional_headers
    return [
        header for header in actual_headers 
        if header and header not in all_known
    ]


def _check_optional_present(
    actual_headers: list, optional_headers: list
) -> str:
    """Check for present optional columns and return warning if any."""
    present_optional = [
        column for column in optional_headers if column in actual_headers
    ]
    if present_optional:
        return (
            f"Optional columns detected (will be recalculated): "
            f"{len(present_optional)} columns"
        )
    return None


def _add_missing_error(
    errors: list, actual_headers: list, required_headers: list
) -> None:
    """Add error for missing required columns."""
    missing_required = _check_missing_required(actual_headers, required_headers)
    if missing_required:
        cols_msg = ", ".join(missing_required)
        errors.append(f"Missing required columns: {cols_msg}")


def _add_unknown_warning(
    warnings: list, 
    actual_headers: list, 
    required_headers: list, 
    optional_headers: list
) -> None:
    """Add warning for unknown columns."""
    unknown_columns = _check_unknown_columns(
        actual_headers, required_headers, optional_headers
    )
    if unknown_columns:
        cols_msg = ", ".join(unknown_columns[:5])
        warnings.append(f"Unknown columns (will be ignored): {cols_msg}")
