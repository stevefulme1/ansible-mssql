#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright 2026 Steve Fulmer
# Apache-2.0 (see LICENSE)
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

"""mssql_cdc_info module."""

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r"""
---
module: mssql_cdc_info
short_description: Retrieve cdc information
description:
    - Retrieve details about cdcs.
    - Read-only module.
version_added: "1.0.0"
author:
    - Steve Fulmer (@stevefulme1)
options:
    host:
        description: API host address.
        type: str
        required: true
    table_name:
        description: ID of a specific resource.
        type: str
    name:
        description: Filter by name.
        type: str
    username:
        description: Authentication username.
        type: str
    password:
        description: Authentication password.
        type: str
    api_key:
        description: API key for authentication.
        type: str
    validate_certs:
        description: Validate SSL certificates.
        type: bool
        default: true
  limit:
    description:
      - Maximum number of results to return (maps to SQL TOP/FETCH).
    type: int
    default: 100
  offset:
    description:
      - Number of results to skip (maps to SQL OFFSET).
    type: int
    default: 0
  max_results:
    description:
      - Maximum total results to return.
    type: int
    default: 1000
"""

EXAMPLES = r"""
- name: List all cdcs
  stevefulme1.mssql.mssql_cdc_info:
    host: api.example.com
  register: result

- name: Get a specific cdc
  stevefulme1.mssql.mssql_cdc_info:
    host: api.example.com
    table_name: "example-id"
  register: result
"""

RETURN = r"""
cdcs:
    description: List of resource details.
    returned: always
    type: list
    elements: dict
"""

from ansible.module_utils.basic import AnsibleModule

try:
    from ansible_collections.stevefulme1.mssql.plugins.module_utils.api_client import ApiClient
    HAS_CLIENT = True
except ImportError:
    HAS_CLIENT = False


def main():
    module = AnsibleModule(
        argument_spec=dict(
            table_name=dict(type="str"),
            name=dict(type="str"),
            host=dict(type="str", required=True),
            username=dict(type="str"),
            password=dict(type="str", no_log=True),
            api_key=dict(type="str", no_log=True),
            validate_certs=dict(type="bool", default=True),
            limit=dict(type="int", default=100),
            offset=dict(type="int", default=0),
            max_results=dict(type="int", default=1000),
        ),
        supports_check_mode=True,
    )

    if not HAS_CLIENT:
        module.fail_json(msg="Required Python libraries not found.")

    client = ApiClient(module)
    resource_id = module.params.get("table_name")

    if resource_id:
        result = client.get("cdc", resource_id)
        resources = [result] if result else []
    else:
        _params = dict(module.params)
        if module.params.get("limit"):
            _params["limit"] = module.params["limit"]
        if module.params.get("offset"):
            _params["offset"] = module.params["offset"]
        resources = client.list("cdc", module.params)

    module.exit_json(changed=False, cdcs=resources)


if __name__ == "__main__":
    main()
