"""Tests for CLI commands using Click's test runner."""

from unittest.mock import patch, MagicMock

from boltzmann_cli.main import cli
from boltzmann_cli.client import AuthError, APIError


class TestLoginCommand:
    def test_saves_key_and_verifies(self, runner, tmp_config):
        mock = MagicMock()
        mock.get.return_value = {"email": "user@example.com"}
        with patch("boltzmann_cli.commands.login.BoltzmannClient", return_value=mock):
            result = runner.invoke(cli, ["login", "--key", "my-api-key"])
        assert result.exit_code == 0
        assert "API key saved" in result.output
        assert "Authenticated as user@example.com" in result.output

    def test_warns_on_verification_failure(self, runner, tmp_config):
        mock = MagicMock()
        mock.get.side_effect = APIError("connection refused")
        with patch("boltzmann_cli.commands.login.BoltzmannClient", return_value=mock):
            result = runner.invoke(cli, ["login", "--key", "bad-key"])
        assert result.exit_code == 0
        assert "API key saved" in result.output
        assert "verification failed" in result.output


class TestProjectsCommand:
    def test_lists_projects(self, runner, tmp_config, mock_client):
        mock_client.get.return_value = {
            "projects": [
                {"id": "proj-1234abcd", "name": "Test Project", "visibility": "private", "created_at": "2026"},
            ]
        }
        with patch("boltzmann_cli.client.BoltzmannClient", return_value=mock_client):
            result = runner.invoke(cli, ["projects", "list"])
        assert result.exit_code == 0
        assert "Test Project" in result.output

    def test_shows_empty_message(self, runner, tmp_config, mock_client):
        mock_client.get.return_value = {"projects": []}
        with patch("boltzmann_cli.client.BoltzmannClient", return_value=mock_client):
            result = runner.invoke(cli, ["projects", "list"])
        assert "No projects found" in result.output


class TestSimulationsCommand:
    def test_lists_simulations(self, runner, tmp_config, mock_client):
        mock_client.get.return_value = {
            "simulations": [
                {"id": "sim-1234abcd", "name": "Sim One", "status": "running", "created_at": "2026"},
            ]
        }
        with patch("boltzmann_cli.client.BoltzmannClient", return_value=mock_client):
            result = runner.invoke(cli, ["simulations", "list"])
        assert result.exit_code == 0
        assert "Sim One" in result.output

    def test_shows_empty_message(self, runner, tmp_config, mock_client):
        mock_client.get.return_value = {"simulations": []}
        with patch("boltzmann_cli.client.BoltzmannClient", return_value=mock_client):
            result = runner.invoke(cli, ["simulations", "list"])
        assert "No simulations found" in result.output


class TestJobsCommand:
    def test_lists_jobs(self, runner, tmp_config, mock_client):
        mock_client.get.return_value = {
            "jobs": [
                {"id": "job-1234abcd", "status": "completed", "type": "sweep", "created_at": "2026"},
            ]
        }
        with patch("boltzmann_cli.client.BoltzmannClient", return_value=mock_client):
            result = runner.invoke(cli, ["jobs", "list"])
        assert result.exit_code == 0
        assert "completed" in result.output


class TestApiKeysCommand:
    def test_lists_api_keys(self, runner, tmp_config, mock_client):
        mock_client.token = None
        mock_client.api_key = "k"
        mock_client.get.return_value = [
            {
                "id": "key-1234abcd",
                "name": "CI key",
                "key_prefix": "bz_",
                "status": "active",
                "last_used_at": None,
                "request_count": 3,
                "expires_at": None,
            }
        ]
        with patch("boltzmann_cli.client.BoltzmannClient", return_value=mock_client):
            result = runner.invoke(cli, ["api-keys", "list"])
        assert result.exit_code == 0
        assert "CI key" in result.output


class TestAuthCommand:
    def test_status_authenticated(self, runner, tmp_config, mock_client):
        mock_client.token = None
        mock_client.api_key = "k"
        mock_client.get.return_value = {"email": "user@example.com", "sub": "u1"}
        with patch("boltzmann_cli.client.BoltzmannClient", return_value=mock_client):
            result = runner.invoke(cli, ["auth", "status"])
        assert result.exit_code == 0
        assert "user@example.com" in result.output


class TestVersionFlag:
    def test_version(self, runner):
        result = runner.invoke(cli, ["--version"])
        assert result.exit_code == 0
        assert "boltzmann" in result.output


class TestGlobalFlags:
    def test_verbose_accepted(self, runner, tmp_config, mock_client):
        mock_client.get.return_value = {"projects": []}
        with patch("boltzmann_cli.client.BoltzmannClient", return_value=mock_client):
            result = runner.invoke(cli, ["--verbose", "projects", "list"])
        assert result.exit_code == 0

    def test_debug_accepted(self, runner, tmp_config, mock_client):
        mock_client.get.return_value = {"projects": []}
        with patch("boltzmann_cli.client.BoltzmannClient", return_value=mock_client):
            result = runner.invoke(cli, ["--debug", "projects", "list"])
        assert result.exit_code == 0

    def test_ci_accepted(self, runner, tmp_config, mock_client):
        mock_client.get.return_value = {"projects": []}
        with patch("boltzmann_cli.client.BoltzmannClient", return_value=mock_client):
            result = runner.invoke(cli, ["--ci", "projects", "list"])
        assert result.exit_code == 0

    def test_ci_auto_detected_from_env(self, runner, tmp_config, mock_client):
        mock_client.get.return_value = {"projects": []}
        with patch("boltzmann_cli.client.BoltzmannClient", return_value=mock_client):
            result = runner.invoke(cli, ["projects", "list"], env={"CI": "true"})
        assert result.exit_code == 0


class TestCompletionCommand:
    def test_prints_zsh_script(self, runner):
        result = runner.invoke(cli, ["completion", "zsh"])
        assert result.exit_code == 0
        assert "_BOLTZMANN_COMPLETE" in result.output
        assert "boltzmann" in result.output
