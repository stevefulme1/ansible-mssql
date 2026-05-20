#!/usr/bin/python
# -*- coding: utf-8 -*-
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r"""
---
module: mssql_login_info
short_description: Gather information about SQL Server logins
description:
  - Returns information about server-level logins on a Microsoft SQL Server instance.
  - Queries the C(sys.server_principals) system view.
version_added: "0.1.0"
options:
  name:
    description:
      - Name of a specific login to query.
      - If omitted, returns info for all SQL and Windows logins.
    type: str
extends_documentation_fragment:
  - stevefulme1.mssql.mssql
author:
  - Steve Fulmer (@stevefulme1)
"""

EXAMPLES = r"""
- name: Get all login info
  stevefulme1.mssql.mssql_login_info:
    login_host: sqlserver.example.com
    login_user: sa
    login_password: MyP@ssw0rd
  register: login_info

- name: Get info for a specific login
  stevefulme1.mssql.mssql_login_info:
    login_host: sqlserver.example.com
    login_user: sa
    login_password: MyP@ssw0rd
    name: app_user
  register: login_info
"""

RETURN = r"""
logins:
  description: List of login information dictionaries.
  returned: always
  type: list
  elements: dict
  contains:
    name:
      description: Login name.
      type: str
    principal_id:
      description: Principal ID.
      type: int
    type_desc:
      description: Principal type description.
      type: str
    is_disabled:
      description: Whether the login is disabled.
      type: bool
    default_database_name:
      description: Default database.
      type: str
"""

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.stevefulme1.mssql.plugins.module_utils.mssql_client import (
    MSSQLClient,
    mssql_common_argument_spec,
)


def main():
    argument_spec = mssql_common_argument_spec()
    argument_spec.update(
        name=dict(type='str'),
    )
    module = AnsibleModule(
        argument_spec=argument_spec,
        supports_check_mode=True,
    )

    name = module.params.get('name')
    client = MSSQLClient(module)

    try:
        query = (
            "SELECT name, principal_id, type_desc, is_disabled, "
            "default_database_name, default_language_name, "
            "create_date, modify_date "
            "FROM sys.server_principals WHERE type IN ('S', 'U')"
        )
        params = None
        if name:
            query += " AND name = %s"
            params = (name,)

        rows = client.execute_query(query, params)
        # Convert datetime objects to strings for JSON serialization
        for row in rows:
            for key in ('create_date', 'modify_date'):
                if key in row and row[key] is not None:
                    row[key] = str(row[key])
        module.exit_json(changed=False, logins=rows)
    finally:
        client.close()


if __name__ == '__main__':
    main()
