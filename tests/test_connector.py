"""Unit tests for the connector's collect/filter logic.

OpenSourceMalwareConnector.__init__ instantiates an OpenCTIConnectorHelper
(needs a live OpenCTI), so we build the instance with __new__ and inject mocks
to exercise _collect() in isolation.
"""

from types import SimpleNamespace
from unittest.mock import MagicMock

from connector import OpenSourceMalwareConnector


def _connector(verified_only, threats):
    conn = OpenSourceMalwareConnector.__new__(OpenSourceMalwareConnector)
    conn.helper = SimpleNamespace(
        connector_logger=SimpleNamespace(info=lambda *a, **k: None)
    )
    conn.config = SimpleNamespace(ecosystems=["npm"], verified_only=verified_only)
    conn.client = SimpleNamespace(query_latest=lambda ecosystem: threats)
    # Each threat maps to a single sentinel STIX object named by its id.
    conn.converter = SimpleNamespace(
        author="AUTHOR",
        threat_to_stix=MagicMock(side_effect=lambda t, e: [f"stix:{t['id']}"]),
    )
    return conn


def test_collect_always_includes_author_first():
    conn = _connector(verified_only=False, threats=[])
    assert conn._collect() == ["AUTHOR"]


def test_collect_includes_all_when_verified_only_false():
    threats = [
        {"id": "a", "status": "verified"},
        {"id": "b", "status": "pending"},
    ]
    conn = _connector(verified_only=False, threats=threats)
    assert conn._collect() == ["AUTHOR", "stix:a", "stix:b"]


def test_collect_skips_unverified_when_verified_only_true():
    threats = [
        {"id": "a", "status": "verified"},
        {"id": "b", "status": "pending"},
        {"id": "c"},  # missing status -> skipped
    ]
    conn = _connector(verified_only=True, threats=threats)
    assert conn._collect() == ["AUTHOR", "stix:a"]
