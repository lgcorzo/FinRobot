"""Tests for IO osvariables module."""

import pytest
from unittest.mock import patch
from finrobot.infrastructure.io.osvariables import Env


class TestEnv:
    """Test suite for Env environment variable class."""

    @pytest.fixture(autouse=True)
    def clear_singleton(self):
        """Clear the Singleton instance before and after each test."""
        from finrobot.infrastructure.io.osvariables import Singleton

        Singleton._instances = {}
        yield
        Singleton._instances = {}

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
        with patch.dict("os.environ", {}, clear=True):
            # Also need to make sure we don't load from .env file during tests
            with patch.object(Env, "model_config", {"case_sensitive": False}):
                env = Env()

                # Defaults are local paths, not remote URIs
                assert env.mlflow_tracking_uri == "./mlruns"
                assert env.mlflow_registry_uri == "./mlruns"
                assert env.mlflow_experiment_name == "finrobot"
                assert env.mlflow_registered_model_name == "finrobot"

    def test_env_aws_defaults(self):
        """Test that AWS-related fields have defaults."""
        with patch.dict("os.environ", {}, clear=True):
            with patch.object(Env, "model_config", {"case_sensitive": False}):
                env = Env()

                # These should have empty string defaults
                assert env.aws_access_key_id == ""
                assert env.aws_secret_access_key == ""
