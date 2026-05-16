# -*- coding: utf-8 -*-
# Copyright 2026 Steve Fulmer
# Apache-2.0 (see LICENSE)
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

"""mssql dynamic inventory plugin."""

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = r"""
---
name: mssql_inventory
short_description: SQL Server instances
description:
    - Dynamically discovers SQL Server instances.
    - Returns hosts with metadata as host variables.
version_added: "1.0.0"
author:
    - Steve Fulmer (@stevefulme1)
options:
    host:
        description: API host address.
        type: str
        required: true
        env:
            - name: MSSQL_HOST
    api_key:
        description: API key for authentication.
        type: str
        env:
            - name: MSSQL_API_KEY
    username:
        description: Authentication username.
        type: str
        env:
            - name: MSSQL_USERNAME
    password:
        description: Authentication password.
        type: str
        env:
            - name: MSSQL_PASSWORD
    validate_certs:
        description: Validate SSL certificates.
        type: bool
        default: true
"""

EXAMPLES = r"""
# mssql_inventory.yml
plugin: stevefulme1.mssql.mssql_inventory
host: api.example.com
api_key: "{{ lookup('env', 'MSSQL_API_KEY') }}"
"""

from ansible.plugins.inventory import BaseInventoryPlugin

try:
    import requests

    HAS_REQUESTS = True
except ImportError:
    HAS_REQUESTS = False


class InventoryModule(BaseInventoryPlugin):
    NAME = "stevefulme1.mssql.mssql_inventory"

    def verify_file(self, path):
        if super().verify_file(path):
            return path.endswith(("mssql_inventory.yml", "mssql_inventory.yaml"))
        return False

    def parse(self, inventory, loader, path, cache=True):
        super().parse(inventory, loader, path, cache)
        self._read_config_data(path)

        if not HAS_REQUESTS:
            raise Exception("requests library is required")

        host = self.get_option("host")
        api_key = self.get_option("api_key")
        self.inventory.add_group("mssql")

        # Discovery logic - connect to API and populate inventory
        try:
            headers = {"Authorization": f"Bearer {api_key}"} if api_key else {}
            resp = requests.get(
                f"https://{host}/api/v1/hosts",
                headers=headers,
                verify=self.get_option("validate_certs"),
                timeout=30,
            )
            resp.raise_for_status()
            for item in resp.json().get("data", []):
                hostname = item.get("name", item.get("hostname", item.get("id", "")))
                if hostname:
                    self.inventory.add_host(hostname, group="mssql")
                    for k, v in item.items():
                        self.inventory.set_variable(hostname, k, v)
        except Exception as e:
            self.display.warning(f"Failed to discover hosts: {e}")
