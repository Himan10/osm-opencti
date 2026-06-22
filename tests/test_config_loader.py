"""Unit tests for ConfigConnector — driven purely by env vars (which take
precedence over config.yml), so they're deterministic in CI."""

import pytest

from config_loader import ConfigConnector

_ENV_KEYS = [
    "OPENSOURCEMALWARE_API_BASE_URL",
    "OPENSOURCEMALWARE_API_TOKEN",
    "OPENSOURCEMALWARE_ECOSYSTEMS",
    "OPENSOURCEMALWARE_LABEL",
    "OPENSOURCEMALWARE_VERIFIED_ONLY",
]


@pytest.fixture(autouse=True)
def _clean_env(monkeypatch):
    # Start from a known-empty slate so defaults are exercised predictably.
    for key in _ENV_KEYS:
        monkeypatch.delenv(key, raising=False)


def test_defaults(monkeypatch):
    monkeypatch.setenv("OPENSOURCEMALWARE_API_TOKEN", "tok")
    config = ConfigConnector()
    assert config.api_base_url == "https://api.opensourcemalware.com/functions/v1"
    assert config.ecosystems == ["npm", "pypi"]
    assert config.label == "opensourcemalware"
    assert config.api_token == "tok"


def test_ecosystems_csv_is_parsed_and_trimmed(monkeypatch):
    monkeypatch.setenv("OPENSOURCEMALWARE_API_TOKEN", "tok")
    monkeypatch.setenv("OPENSOURCEMALWARE_ECOSYSTEMS", " npm , pypi , ")
    config = ConfigConnector()
    # Whitespace trimmed and empty entries dropped.
    assert config.ecosystems == ["npm", "pypi"]


def test_label_override(monkeypatch):
    monkeypatch.setenv("OPENSOURCEMALWARE_API_TOKEN", "tok")
    monkeypatch.setenv("OPENSOURCEMALWARE_LABEL", "custom-label")
    assert ConfigConnector().label == "custom-label"
