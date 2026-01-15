"""Tests for IO osvariables module."""

from finrobot.infrastructure.io.osvariables import Env


class TestEnv:
    """Test suite for Env environment variable class."""

    def test_env_instantiation(self):
        """Test that Env can be instantiated."""
        env = Env()
        assert env is not None

    def test_env_singleton(self):
        """Test that Env is a singleton."""
        env1 = Env()
        env2 = Env()
        assert env1 is env2

    def test_env_default_values(self):
        """Test that Env has expected default values."""
        env = Env()

        # Defaults are local paths, not remote URIs
        assert env.mlflow_tracking_uri == "./mlruns"
        assert env.mlflow_registry_uri == "./mlruns"
        assert env.mlflow_experiment_name == "finrobot"
        assert env.mlflow_registered_model_name == "finrobot"

    def test_env_aws_defaults(self):
        """Test that AWS-related fields have defaults."""
        env = Env()

        # These should have empty string defaults
        assert env.aws_access_key_id == ""
        assert env.aws_secret_access_key == ""
