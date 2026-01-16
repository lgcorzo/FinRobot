"""Tests for LoggerService."""

from unittest.mock import patch

from finrobot.infrastructure.services.logger_service import LoggerService


class TestLoggerService:
    """Test suite for LoggerService."""

    def test_logger_service_instantiation(self) -> None:
        """Test that LoggerService can be instantiated with defaults."""
        service = LoggerService()
        assert service.level == "DEBUG"
        assert service.sink == "stderr"

    def test_logger_service_custom_level(self) -> None:
        """Test LoggerService with custom log level."""
        service = LoggerService(level="INFO")
        assert service.level == "INFO"

    @patch("finrobot.infrastructure.services.logger_service.TracerProvider")
    @patch("finrobot.infrastructure.services.logger_service.LoggerProvider")
    def test_logger_service_start(self, mock_logger_provider, mock_tracer_provider) -> None:  # type: ignore[no-untyped-def]
        """Test that start() initializes OpenTelemetry providers."""
        service = LoggerService()
        service.start()

        mock_tracer_provider.assert_called_once()
        mock_logger_provider.assert_called_once()

    def test_logger_service_logger_returns_loguru(self) -> None:
        """Test that logger() returns a loguru logger instance."""
        service = LoggerService()
        service.start()
        logger = service.logger()

        # Verify it's a loguru logger by checking for expected methods
        assert hasattr(logger, "info")
        assert hasattr(logger, "debug")
        assert hasattr(logger, "error")
        assert hasattr(logger, "warning")

    def test_logger_service_stop(self) -> None:
        """Test that stop() completes without error."""
        service = LoggerService()
        service.start()
        # stop() should not raise
        service.stop()
