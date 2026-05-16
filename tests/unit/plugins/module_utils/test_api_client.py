from __future__ import absolute_import, division, print_function
__metaclass__ = type

"""API client tests."""


TestApiClient:
    def test_auth(self):
        headers = dict()
        headers["Authorization"] = "Bearer test"
        assert "Authorization" in headers
