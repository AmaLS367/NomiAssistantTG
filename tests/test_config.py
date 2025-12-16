import pytest
import os
from unittest.mock import patch
from core.config import get_settings, ConfigError

def test_config_valid():
    """Ensure settings are loaded correctly from env vars."""
    env_vars = {
        "TELEGRAM_BOT_TOKEN": "123:ABC",
        "NOMI_API_KEY": "sk-test",
        "REQUEST_TIMEOUT_SEC": "10",
        "VOSK_MODEL_PATH": "/tmp/model"
    }
    with patch.dict(os.environ, env_vars, clear=True):
        settings = get_settings()
        assert settings.telegram_bot_token == "123:ABC"
        assert settings.request_timeout_sec == 10.0

def test_config_missing_token():
    """Ensure ConfigError is raised when critical vars are missing."""
    with patch.dict(os.environ, {}, clear=True):
        with pytest.raises(ConfigError, match="TELEGRAM_BOT_TOKEN is missing"):
            get_settings()

def test_config_missing_api_key():
    """Ensure ConfigError is raised when NOMI_API_KEY is missing."""
    env_vars = {
        "TELEGRAM_BOT_TOKEN": "123:ABC",
    }
    with patch.dict(os.environ, env_vars, clear=True):
        with pytest.raises(ConfigError, match="NOMI_API_KEY is missing"):
            get_settings()

