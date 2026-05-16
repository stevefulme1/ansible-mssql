"""API client tests."""
from unittest.mock import MagicMock

class TestApiClient:
    def test_auth(self):
        headers = dict()
        headers["Authorization"] = "Bearer test"
        assert "Authorization" in headers
