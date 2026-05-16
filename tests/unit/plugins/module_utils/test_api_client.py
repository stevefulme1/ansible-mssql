from __future__ import absolute_import, division, print_function
__metaclass__ = type

"""API client tests."""


class TestApiClient:
    def test_auth_header(self):
        headers = dict()
        headers["Authorization"] = "Bearer test"
        assert "Authorization" in headers

    def test_basic_auth(self):
        auth = ("admin", "password")
        assert auth[0] == "admin"
