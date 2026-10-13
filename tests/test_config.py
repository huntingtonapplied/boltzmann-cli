"""Tests for the config module."""

import os
import pytest
from unittest.mock import patch

from boltzmann_cli.config import (
    load_config,
    save_config,
    get_api_key,
    get_api_url,
    set_api_key,
    set_api_url,
    DEFAULT_API_URL,
)


class TestLoadConfig:
    def test_returns_empty_dict_when_no_file(self, tmp_path):
        config_file = tmp_path / "config.yaml"
        with patch("boltzmann_cli.config.CONFIG_FILE", config_file):
            assert load_config() == {}

    def test_loads_existing_config(self, tmp_path):
        config_file = tmp_path / "config.yaml"
        config_file.write_text("api_key: my-key\napi_url: http://localhost\n")
        with patch("boltzmann_cli.config.CONFIG_FILE", config_file):
            config = load_config()
            assert config["api_key"] == "my-key"
            assert config["api_url"] == "http://localhost"

    def test_handles_empty_file(self, tmp_path):
        config_file = tmp_path / "config.yaml"
        config_file.write_text("")
        with patch("boltzmann_cli.config.CONFIG_FILE", config_file):
            assert load_config() == {}


class TestSaveConfig:
    def test_creates_config_file(self, tmp_path):
        config_dir = tmp_path / ".boltzmann"
        config_file = config_dir / "config.yaml"
        with patch("boltzmann_cli.config.CONFIG_DIR", config_dir), \
             patch("boltzmann_cli.config.CONFIG_FILE", config_file):
            save_config({"api_key": "test-key"})
            assert config_file.exists()
            assert "test-key" in config_file.read_text()

    def test_overwrites_existing(self, tmp_path):
        config_dir = tmp_path / ".boltzmann"
        config_dir.mkdir()
        config_file = config_dir / "config.yaml"
        config_file.write_text("api_key: old\n")
        with patch("boltzmann_cli.config.CONFIG_DIR", config_dir), \
             patch("boltzmann_cli.config.CONFIG_FILE", config_file):
            save_config({"api_key": "new"})
            content = config_file.read_text()
            assert "new" in content
            assert "old" not in content


class TestGetApiKey:
    def test_env_var_takes_precedence(self, tmp_path):
        config_file = tmp_path / "config.yaml"
        config_file.write_text("api_key: file-key\n")
        with patch("boltzmann_cli.config.CONFIG_FILE", config_file), \
             patch.dict(os.environ, {"BOLTZMANN_API_KEY": "env-key"}):
            assert get_api_key() == "env-key"

    def test_falls_back_to_config(self, tmp_path):
        config_file = tmp_path / "config.yaml"
        config_file.write_text("api_key: file-key\n")
        env = os.environ.copy()
        env.pop("BOLTZMANN_API_KEY", None)
        with patch("boltzmann_cli.config.CONFIG_FILE", config_file), \
             patch.dict(os.environ, env, clear=True):
            assert get_api_key() == "file-key"

    def test_returns_none_when_unset(self, tmp_path):
        config_file = tmp_path / "nonexistent.yaml"
        env = os.environ.copy()
        env.pop("BOLTZMANN_API_KEY", None)
        with patch("boltzmann_cli.config.CONFIG_FILE", config_file), \
             patch.dict(os.environ, env, clear=True):
            assert get_api_key() is None


class TestGetApiUrl:
    def test_returns_default_when_unset(self, tmp_path):
        config_file = tmp_path / "nonexistent.yaml"
        env = os.environ.copy()
        env.pop("BOLTZMANN_API_URL", None)
        with patch("boltzmann_cli.config.CONFIG_FILE", config_file), \
             patch.dict(os.environ, env, clear=True):
            assert get_api_url() == DEFAULT_API_URL

    def test_env_var_overrides(self):
        with patch.dict(os.environ, {"BOLTZMANN_API_URL": "http://custom"}):
            assert get_api_url() == "http://custom"


class TestSetters:
    def test_set_api_key_persists(self, tmp_path):
        config_dir = tmp_path / ".boltzmann"
        config_file = config_dir / "config.yaml"
        with patch("boltzmann_cli.config.CONFIG_DIR", config_dir), \
             patch("boltzmann_cli.config.CONFIG_FILE", config_file):
            set_api_key("my-new-key")
            assert load_config()["api_key"] == "my-new-key"

    def test_set_api_key_preserves_other_fields(self, tmp_path):
        config_dir = tmp_path / ".boltzmann"
        config_dir.mkdir()
        config_file = config_dir / "config.yaml"
        config_file.write_text("api_url: http://custom\n")
        with patch("boltzmann_cli.config.CONFIG_DIR", config_dir), \
             patch("boltzmann_cli.config.CONFIG_FILE", config_file):
            set_api_key("my-key")
            config = load_config()
            assert config["api_key"] == "my-key"
            assert config["api_url"] == "http://custom"

    def test_set_api_url_persists(self, tmp_path):
        config_dir = tmp_path / ".boltzmann"
        config_file = config_dir / "config.yaml"
        with patch("boltzmann_cli.config.CONFIG_DIR", config_dir), \
             patch("boltzmann_cli.config.CONFIG_FILE", config_file):
            set_api_url("http://example:8009")
            assert load_config()["api_url"] == "http://example:8009"
