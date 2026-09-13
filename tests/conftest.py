"""Public HTTP probes belong to acquisition commands, never the offline suite."""
import pytest
import requests


@pytest.fixture(autouse=True)
def block_unmocked_requests(monkeypatch):
    def blocked(*args, **kwargs):
        raise AssertionError('Offline tests must inject HTTP transport')
    monkeypatch.setattr(requests.sessions.Session, 'request', blocked)
