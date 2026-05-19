# -*- coding: utf-8 -*-
# Copyright 2026 Steve Fulmer
# Apache-2.0 (see LICENSE)
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

"""Shared API client for mssql collection."""

from __future__ import absolute_import, division, print_function
__metaclass__ = type

try:
    import requests
    HAS_REQUESTS = True
except ImportError:
    HAS_REQUESTS = False


class ApiClient:
    """REST API client for Mssql."""

    _CONNECTION_KEYS = frozenset({
        "host", "username", "password", "api_key",
        "validate_certs", "timeout", "state",
    })

    def __init__(self, module):
        self.module = module
        self.host = module.params["host"]
        self.validate_certs = module.params.get("validate_certs", True)
        self.session = requests.Session()
        self.session.verify = self.validate_certs
        self._authenticate()

    def _authenticate(self):
        api_key = self.module.params.get("api_key")
        username = self.module.params.get("username")
        password = self.module.params.get("password")
        if api_key:
            self.session.headers["Authorization"] = f"Bearer {api_key}"
        elif username and password:
            self.session.auth = (username, password)

    def _url(self, endpoint):
        return f"https://{self.host}/api/v1/{endpoint}"

    def _filter_params(self, params):
        """Strip connection/auth keys so credentials never leak into API bodies."""
        return {k: v for k, v in params.items() if k not in self._CONNECTION_KEYS}

    def get(self, resource_type, resource_id):
        resp = self.session.get(self._url(f"{resource_type}s/{resource_id}"), timeout=30)
        if resp.status_code == 404:
            return None
        resp.raise_for_status()
        return resp.json()

    def list(self, resource_type, params=None):
        resp = self.session.get(self._url(f"{resource_type}s"), params=params or {}, timeout=30)
        resp.raise_for_status()
        data = resp.json()
        return data.get("data", data.get("items", data if isinstance(data, list) else []))

    def create(self, resource_type, params):
        resp = self.session.post(self._url(f"{resource_type}s"), json=self._filter_params(params), timeout=30)
        resp.raise_for_status()
        return resp.json()

    def update(self, resource_type, resource_id, params):
        resp = self.session.put(self._url(f"{resource_type}s/{resource_id}"), json=self._filter_params(params), timeout=30)
        resp.raise_for_status()
        return resp.json()

    def delete(self, resource_type, resource_id):
        resp = self.session.delete(self._url(f"{resource_type}s/{resource_id}"), timeout=30)
        if resp.status_code == 404:
            return
        resp.raise_for_status()
