#!/usr/bin/python
# -*- coding: utf-8 -*-
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-only

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r"""
---
module: mssql_permission_info
short_description: Gather SQL Server database permission information
description:
  - Returns information about permissions on a SQL Server database.
  - Queries sys.database_permissions and related views.
version_added: "0.1.0"
options:
  principal:
    description:
      - Filter by principal (user or role).
      - If omitted, returns all permissions.
    type: str
  securable:
    description:
      - Filter by securable (e.g., schema, object).
      - If omitted, returns permissions on all securables.
    type: str
extends_documentation_fragment:
  - stevefulme1.mssql.mssql
author:
  - Steve Fulmer (@stevefulme1)
"""

EXAMPLES = r"""
- name: Get all database permissions
  stevefulme1.mssql.mssql_permission_info:
    login_host: sqlserver.example.com
    login_user: sa
    login_password: MyP@ssw0rd
    database: myappdb
  register: perm_info

- name: Get permissions for a specific principal
  stevefulme1.mssql.mssql_permission_info:
    login_host: sqlserver.example.com
    login_user: sa
    login_password: MyP@ssw0rd
    database: myappdb
    principal: app_user
  register: perm_info
"""

RETURN = r"""
permissions:
  description: List of permission dictionaries.
  returned: always
  type: list
  elements: dict
  contains:
    principal:
      description: Principal name.
      type: str
    permission:
      description: Permission name.
      type: str
    state:
      description: Permission state (GRANT, DENY).
      type: str
    securable:
      description: Securable name.
      type: str
    securable_type:
      description: Securable type.
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
        principal=dict(type='str'),
        securable=dict(type='str'),
    )
    module = AnsibleModule(
        argument_spec=argument_spec,
        supports_check_mode=True,
    )

    principal = module.params.get('principal')
    securable = module.params.get('securable')
    client = MSSQLClient(module)

    try:
        query = """
            SELECT
                USER_NAME(dp.grantee_principal_id) AS principal,
                dp.permission_name AS permission,
                dp.state_desc AS state,
                OBJECT_NAME(dp.major_id) AS securable,
                dp.class_desc AS securable_type
            FROM sys.database_permissions dp
            WHERE 1=1
        """
        params = []

        if principal:
            query += " AND USER_NAME(dp.grantee_principal_id) = %s"
            params.append(principal)

        if securable:
            query += " AND OBJECT_NAME(dp.major_id) = %s"
            params.append(securable)

        rows = client.execute_query(query, params if params else None)
        module.exit_json(changed=False, permissions=rows)
    finally:
        client.close()


if __name__ == '__main__':
    main()
