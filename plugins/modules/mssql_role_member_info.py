#!/usr/bin/python
# -*- coding: utf-8 -*-
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-only

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r"""
---
module: mssql_role_member_info
short_description: Gather SQL Server database role membership information
description:
  - Returns information about database role membership.
  - Queries sys.database_role_members and sys.database_principals.
version_added: "0.1.0"
options:
  role:
    description:
      - Filter by role name.
      - If omitted, returns all role memberships.
    type: str
  member:
    description:
      - Filter by member name.
      - If omitted, returns all members.
    type: str
extends_documentation_fragment:
  - stevefulme1.mssql.mssql
author:
  - Steve Fulmer (@stevefulme1)
"""

EXAMPLES = r"""
- name: Get all role memberships
  stevefulme1.mssql.mssql_role_member_info:
    login_host: sqlserver.example.com
    login_user: sa
    login_password: MyP@ssw0rd
    database: myappdb
  register: role_info

- name: Get members of a specific role
  stevefulme1.mssql.mssql_role_member_info:
    login_host: sqlserver.example.com
    login_user: sa
    login_password: MyP@ssw0rd
    database: myappdb
    role: db_datareader
  register: role_info

- name: Get roles for a specific member
  stevefulme1.mssql.mssql_role_member_info:
    login_host: sqlserver.example.com
    login_user: sa
    login_password: MyP@ssw0rd
    database: myappdb
    member: app_user
  register: role_info
"""

RETURN = r"""
role_members:
  description: List of role membership dictionaries.
  returned: always
  type: list
  elements: dict
  contains:
    role:
      description: Role name.
      type: str
    member:
      description: Member name.
      type: str
    member_principal_id:
      description: Member principal ID.
      type: int
"""

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.stevefulme1.mssql.plugins.module_utils.mssql_client import (
    MSSQLClient,
    mssql_common_argument_spec,
)


def main():
    argument_spec = mssql_common_argument_spec()
    argument_spec.update(
        role=dict(type='str'),
        member=dict(type='str'),
    )
    module = AnsibleModule(
        argument_spec=argument_spec,
        supports_check_mode=True,
    )

    role = module.params.get('role')
    member = module.params.get('member')
    client = MSSQLClient(module)

    try:
        query = """
            SELECT
                role_p.name AS role,
                member_p.name AS member,
                drm.member_principal_id
            FROM sys.database_role_members drm
            JOIN sys.database_principals role_p ON drm.role_principal_id = role_p.principal_id
            JOIN sys.database_principals member_p ON drm.member_principal_id = member_p.principal_id
            WHERE 1=1
        """
        params = []

        if role:
            query += " AND role_p.name = %s"
            params.append(role)

        if member:
            query += " AND member_p.name = %s"
            params.append(member)

        rows = client.execute_query(query, params if params else None)
        module.exit_json(changed=False, role_members=rows)
    finally:
        client.close()


if __name__ == '__main__':
    main()
