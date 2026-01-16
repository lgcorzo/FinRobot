"""Tests for MlflowService."""

from unittest.mock import MagicMock, patch

from finrobot.infrastructure.services.mlflow_service import MlflowService


class TestMlflowService:
    """Test suite for MlflowService."""

    def test_mlflow_service_instantiation(self) -> None:
        """Test that MlflowService can be instantiated."""
        service = MlflowService()
        assert service is not None
        # Should have tracking_uri from Env defaults
        assert service.tracking_uri is not None
        assert service.experiment_name is not None

    def test_mlflow_service_custom_config(self) -> None:
        """Test MlflowService with custom configuration."""
        service = MlflowService(tracking_uri="http://custom:5000", experiment_name="custom_experiment")
        assert service.tracking_uri == "http://custom:5000"
        assert service.experiment_name == "custom_experiment"

    @patch("finrobot.infrastructure.services.mlflow_service.mlflow")
    def test_mlflow_service_start_calls_mlflow(self, mock_mlflow) -> None:  # type: ignore[no-untyped-def]
        """Test that start() calls MLflow methods."""
        service = MlflowService(
            tracking_uri="http://test:5000",
            registry_uri="http://test:5000",
            experiment_name="test_exp",
        )
        service.start()

        mock_mlflow.set_tracking_uri.assert_called_once()
        mock_mlflow.set_registry_uri.assert_called_once()
        mock_mlflow.set_experiment.assert_called_once()
        mock_mlflow.autolog.assert_called_once()

    @patch("finrobot.infrastructure.services.mlflow_service.mlflow")
    def test_mlflow_service_run_context(self, mock_mlflow) -> None:  # type: ignore[no-untyped-def]
        """Test that run_context() creates an MLflow run."""
        mock_run = MagicMock()
        mock_mlflow.start_run.return_value.__enter__ = MagicMock(return_value=mock_run)
        mock_mlflow.start_run.return_value.__exit__ = MagicMock(return_value=False)

        service = MlflowService()
        run_config = MlflowService.RunConfig(name="test_run")

        with service.run_context(run_config=run_config) as run:
            mock_mlflow.start_run.assert_called()

    def test_mlflow_service_stop(self) -> None:
        """Test that stop() completes without error."""
        service = MlflowService()
        # stop() should not raise
        service.stop()
