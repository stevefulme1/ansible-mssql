#!/usr/bin/python
# -*- coding: utf-8 -*-
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r"""
---
module: mssql_user_info
short_description: Gather information about SQL Server database users
description:
  - Returns information about database-level users on a Microsoft SQL Server instance.
  - Queries the C(sys.database_principals) system view.
version_added: "0.1.0"
options:
  name:
    description:
      - Name of a specific user to query.
      - If omitted, returns info for all users in the database.
    type: str
extends_documentation_fragment:
  - stevefulme1.mssql.mssql
author:
  - Steve Fulmer (@stevefulme1)
"""

EXAMPLES = r"""
- name: Get all database users
  stevefulme1.mssql.mssql_user_info:
    login_host: sqlserver.example.com
    login_user: sa
    login_password: MyP@ssw0rd
    database: myappdb
  register: user_info

- name: Get info for a specific user
  stevefulme1.mssql.mssql_user_info:
    login_host: sqlserver.example.com
    login_user: sa
    login_password: MyP@ssw0rd
    database: myappdb
    name: app_user
  register: user_info
"""

RETURN = r"""
users:
  description: List of user information dictionaries.
  returned: always
  type: list
  elements: dict
  contains:
    name:
      description: User name.
      type: str
    principal_id:
      description: Principal ID.
      type: int
    type_desc:
      description: Principal type description.
      type: str
    default_schema_name:
      description: Default schema.
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
            "SELECT dp.name, dp.principal_id, dp.type_desc, dp.default_schema_name, "
            "dp.create_date, dp.modify_date "
            "FROM sys.database_principals dp "
            "WHERE dp.type IN ('S', 'U', 'E', 'X')"
        )
        params = None
        if name:
            query += " AND dp.name = %s"
            params = (name,)

        rows = client.execute_query(query, params)
        for row in rows:
            for key in ('create_date', 'modify_date'):
                if key in row and row[key] is not None:
                    row[key] = str(row[key])
        module.exit_json(changed=False, users=rows)
    finally:
        client.close()


if __name__ == '__main__':
    main()
