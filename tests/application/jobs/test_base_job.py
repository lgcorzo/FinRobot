"""Tests for base Job class."""

import typing as T
from unittest.mock import patch

import pytest

from finrobot.application.jobs.base import Job


class ConcreteJob(Job):
    """Concrete implementation of Job for testing."""

    KIND: T.Literal["test"] = "test"
    test_param: str = "default"

    def run(self) -> dict:
        logger = self.logger_service.logger()
        logger.info(f"Running test job with param: {self.test_param}")
        return {"result": "success", "param": self.test_param}


class TestJob:
    """Test suite for Job base class."""

    def test_job_instantiation(self):
        """Test that a concrete Job can be instantiated."""
        job = ConcreteJob()
        assert job.KIND == "test"
        assert job.test_param == "default"

    def test_job_custom_params(self):
        """Test Job with custom parameters."""
        job = ConcreteJob(test_param="custom")
        assert job.test_param == "custom"

    def test_job_has_services(self):
        """Test that Job has default services."""
        job = ConcreteJob()
        assert job.logger_service is not None
        assert job.alerts_service is not None
        assert job.mlflow_service is not None

    @patch.object(ConcreteJob, "run", return_value={"result": "mocked"})
    def test_job_run(self, mock_run):
        """Test that run() can be called."""
        job = ConcreteJob()
        result = job.run()

        assert result == {"result": "mocked"}
        mock_run.assert_called_once()

    @patch("finrobot.infrastructure.services.logger_service.LoggerService.start")
    @patch("finrobot.infrastructure.services.alert_service.AlertsService.start")
    @patch("finrobot.infrastructure.services.mlflow_service.MlflowService.start")
    def test_job_context_manager_enter(self, mock_mlflow_start, mock_alerts_start, mock_logger_start):
        """Test that __enter__ starts services."""
        job = ConcreteJob()

        result = job.__enter__()

        mock_logger_start.assert_called_once()
        mock_alerts_start.assert_called_once()
        mock_mlflow_start.assert_called_once()
        assert result is job

    @patch("finrobot.infrastructure.services.mlflow_service.MlflowService.stop")
    @patch("finrobot.infrastructure.services.alert_service.AlertsService.stop")
    @patch("finrobot.infrastructure.services.logger_service.LoggerService.stop")
    @patch("finrobot.infrastructure.services.mlflow_service.MlflowService.start")
    @patch("finrobot.infrastructure.services.alert_service.AlertsService.start")
    @patch("finrobot.infrastructure.services.logger_service.LoggerService.start")
    def test_job_context_manager_exit(
        self,
        mock_logger_start,
        mock_alerts_start,
        mock_mlflow_start,
        mock_logger_stop,
        mock_alerts_stop,
        mock_mlflow_stop,
    ):
        """Test that __exit__ stops services."""
        job = ConcreteJob()
        job.__enter__()  # Need to start first for logger to work

        result = job.__exit__(None, None, None)

        mock_mlflow_stop.assert_called_once()
        mock_alerts_stop.assert_called_once()
        mock_logger_stop.assert_called_once()
        assert result is False  # Should propagate exceptions

    def test_job_frozen(self):
        """Test that Job is frozen (immutable)."""
        job = ConcreteJob()

        with pytest.raises(Exception):  # Pydantic will raise on mutation
            job.test_param = "new_value"
