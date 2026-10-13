"""Shared fixtures for CLI tests."""

import pytest
from unittest.mock import MagicMock, patch
from click.testing import CliRunner


@pytest.fixture
def runner():
    """Click CLI test runner."""
    return CliRunner()


@pytest.fixture
def tmp_config(tmp_path):
    """Redirect config to a temp dir so tests don't touch ~/.boltzmann."""
    config_dir = tmp_path / ".boltzmann"
    config_dir.mkdir()
    config_file = config_dir / "config.yaml"

    with patch("boltzmann_cli.config.CONFIG_DIR", config_dir), \
         patch("boltzmann_cli.config.CONFIG_FILE", config_file):
        yield config_file


@pytest.fixture
def mock_client():
    """A mocked BoltzmannClient that doesn't make real HTTP calls."""
    client = MagicMock()
    client.api_key = "test-key-123"
    client.token = None
    client.api_url = "http://localhost:8009"
    return client
