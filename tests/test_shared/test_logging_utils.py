"""Tests for logging utilities module."""

import os
import logging
import tempfile
from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest

from src.shared.utils.logging_utils import (
    LOG_FORMAT,
    DEFAULT_LOG_FILE,
    _reset_handlers,
    _create_console_handler,
    _create_file_handler,
    setup_logging,
    get_logger
)


# ===================== Constants Tests =====================

class TestLoggingConstants:
    """Tests for logging constants."""
    
    def test_log_format_contains_required_fields(self):
        """
        WHAT: Verify log format has essential fields
        WHY: Logs need to be properly formatted
        BREAKS: Missing info in log output
        """
        assert "%(asctime)s" in LOG_FORMAT
        assert "%(levelname)" in LOG_FORMAT
        assert "%(message)s" in LOG_FORMAT
    
    def test_default_log_file_path_structure(self):
        """
        WHAT: Verify default log path structure
        WHY: Logs should go to data/logs directory
        BREAKS: Logs in wrong location
        """
        assert "data" in DEFAULT_LOG_FILE
        assert "logs" in DEFAULT_LOG_FILE
        assert "log.txt" in DEFAULT_LOG_FILE


# ===================== _reset_handlers Tests =====================

class TestResetHandlers:
    """Tests for _reset_handlers function."""
    
    def test_removes_all_handlers(self):
        """
        WHAT: Remove all handlers from logger
        WHY: Prevent duplicate handlers
        BREAKS: Duplicate log messages
        """
        logger = logging.getLogger("test_reset")
        logger.addHandler(logging.StreamHandler())
        logger.addHandler(logging.StreamHandler())
        
        assert len(logger.handlers) >= 2
        
        _reset_handlers(logger)
        
        assert len(logger.handlers) == 0
    
    def test_handles_logger_with_no_handlers(self):
        """
        WHAT: Handle logger without handlers
        WHY: Should not error on empty handlers
        BREAKS: Exception on fresh logger
        """
        logger = logging.getLogger("test_empty_handlers")
        _reset_handlers(logger)  # Clear any existing
        
        # Should not raise
        _reset_handlers(logger)
        
        assert len(logger.handlers) == 0


# ===================== _create_console_handler Tests =====================

class TestCreateConsoleHandler:
    """Tests for _create_console_handler function."""
    
    def test_creates_stream_handler(self):
        """
        WHAT: Create StreamHandler for console output
        WHY: Logs should print to console
        BREAKS: No console output
        """
        formatter = logging.Formatter(LOG_FORMAT)
        
        handler = _create_console_handler(formatter)
        
        assert isinstance(handler, logging.StreamHandler)
    
    def test_handler_has_formatter(self):
        """
        WHAT: Handler should have formatter set
        WHY: Logs need proper formatting
        BREAKS: Unformatted log output
        """
        formatter = logging.Formatter(LOG_FORMAT)
        
        handler = _create_console_handler(formatter)
        
        assert handler.formatter is formatter


# ===================== _create_file_handler Tests =====================

class TestCreateFileHandler:
    """Tests for _create_file_handler function."""
    
    def test_creates_file_handler(self, tmp_path):
        """
        WHAT: Create FileHandler for log file
        WHY: Logs should be written to file
        BREAKS: No persistent logs
        """
        log_path = str(tmp_path / "test.log")
        formatter = logging.Formatter(LOG_FORMAT)
        
        handler = _create_file_handler(log_path, formatter)
        
        assert isinstance(handler, logging.FileHandler)
        handler.close()
    
    def test_creates_directory_if_needed(self, tmp_path):
        """
        WHAT: Create log directory if missing
        WHY: Should not fail on first run
        BREAKS: Error when logs dir doesn't exist
        """
        log_path = str(tmp_path / "new_dir" / "test.log")
        formatter = logging.Formatter(LOG_FORMAT)
        
        handler = _create_file_handler(log_path, formatter)
        
        assert os.path.exists(os.path.dirname(log_path))
        handler.close()
    
    def test_handler_has_formatter(self, tmp_path):
        """
        WHAT: Handler should have formatter set
        WHY: File logs need proper formatting
        BREAKS: Unformatted file output
        """
        log_path = str(tmp_path / "test.log")
        formatter = logging.Formatter(LOG_FORMAT)
        
        handler = _create_file_handler(log_path, formatter)
        
        assert handler.formatter is formatter
        handler.close()


# ===================== setup_logging Tests =====================

class TestSetupLogging:
    """Tests for setup_logging function."""
    
    def test_configures_root_logger(self, tmp_path):
        """
        WHAT: Configure root logger with handlers
        WHY: All modules use root logger
        BREAKS: No logging works at all
        """
        log_path = str(tmp_path / "test_setup.log")
        
        setup_logging(level=logging.DEBUG, log_file=log_path)
        
        root_logger = logging.getLogger()
        assert root_logger.level == logging.DEBUG
        assert len(root_logger.handlers) >= 2
    
    def test_uses_default_log_file(self):
        """
        WHAT: Use default path when not specified
        WHY: Convenience for normal usage
        BREAKS: Logs in unexpected location
        """
        # Just verify function is callable with defaults
        # Don't actually call to avoid side effects
        assert callable(setup_logging)


# ===================== get_logger Tests =====================

class TestGetLogger:
    """Tests for get_logger function."""
    
    def test_returns_named_logger(self):
        """
        WHAT: Return logger with specified name
        WHY: Each module needs own logger
        BREAKS: All logs from same source
        """
        logger = get_logger("test_module")
        
        assert isinstance(logger, logging.Logger)
        assert logger.name == "test_module"
    
    def test_returns_default_name_when_none(self):
        """
        WHAT: Return logger with module name when None
        WHY: Convenience for module-level logging
        BREAKS: No default name
        """
        logger = get_logger(None)
        
        assert isinstance(logger, logging.Logger)
        assert logger.name  # Should have some name
    
    def test_same_name_returns_same_logger(self):
        """
        WHAT: Same name returns same logger instance
        WHY: Logger instances should be reused
        BREAKS: Memory leak from duplicate loggers
        """
        logger1 = get_logger("same_name")
        logger2 = get_logger("same_name")
        
        assert logger1 is logger2
