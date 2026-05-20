#!/usr/bin/python
# -*- coding: utf-8 -*-
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r"""
---
module: mssql_permission
short_description: Manage SQL Server database permissions
description:
  - Grant, revoke, or deny permissions on a database or database object.
  - Uses T-SQL GRANT, REVOKE, and DENY statements.
version_added: "0.1.0"
options:
  permission:
    description:
      - The permission to manage (e.g. SELECT, INSERT, EXECUTE, CONNECT).
    type: str
    required: true
  securable:
    description:
      - The securable to apply the permission to (e.g. SCHEMA::dbo, OBJECT::dbo.mytable).
      - If omitted, the permission applies at the database level.
    type: str
  principal:
    description:
      - The database user or role to grant/revoke/deny the permission to.
    type: str
    required: true
  state:
    description:
      - The permission state.
    type: str
    choices: [grant, revoke, deny]
    default: grant
  with_grant_option:
    description:
      - Whether the principal can further grant this permission.
      - Only applicable when I(state=grant).
    type: bool
    default: false
extends_documentation_fragment:
  - stevefulme1.mssql.mssql
author:
  - Steve Fulmer (@stevefulme1)
"""

EXAMPLES = r"""
- name: Grant SELECT on a database
  stevefulme1.mssql.mssql_permission:
    login_host: sqlserver.example.com
    login_user: sa
    login_password: MyP@ssw0rd
    database: myappdb
    permission: SELECT
    principal: app_user
    state: grant

- name: Grant EXECUTE on a schema
  stevefulme1.mssql.mssql_permission:
    login_host: sqlserver.example.com
    login_user: sa
    login_password: MyP@ssw0rd
    database: myappdb
    permission: EXECUTE
    securable: "SCHEMA::dbo"
    principal: app_user
    state: grant

- name: Deny DELETE to a user
  stevefulme1.mssql.mssql_permission:
    login_host: sqlserver.example.com
    login_user: sa
    login_password: MyP@ssw0rd
    database: myappdb
    permission: DELETE
    principal: app_user
    state: deny

- name: Revoke INSERT from a user
  stevefulme1.mssql.mssql_permission:
    login_host: sqlserver.example.com
    login_user: sa
    login_password: MyP@ssw0rd
    database: myappdb
    permission: INSERT
    principal: app_user
    state: revoke
"""

RETURN = r"""
permission:
  description: The permission managed.
  returned: always
  type: str
principal:
  description: The principal the permission was applied to.
  returned: always
  type: str
state:
  description: The permission state applied.
  returned: always
  type: str
"""

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.stevefulme1.mssql.plugins.module_utils.mssql_client import (
    MSSQLClient,
    mssql_common_argument_spec,
)


def check_permission(client, permission, principal, on_clause):
    """Check current permission state from sys.database_permissions."""
    query = (
        "SELECT dp.state_desc "
        "FROM sys.database_permissions dp "
        "JOIN sys.database_principals pr ON dp.grantee_principal_id = pr.principal_id "
        "WHERE pr.name = %s AND dp.permission_name = %s"
    )
    params = [principal, permission.upper()]

    if on_clause:
        # For simplicity, check class_desc; database-level perms have class=0
        query += " AND dp.class > 0"
    else:
        query += " AND dp.class = 0"

    rows = client.execute_query(query, tuple(params))
    if rows:
        return rows[0].get('state_desc', '').upper()
    return None


def main():
    argument_spec = mssql_common_argument_spec()
    argument_spec.update(
        permission=dict(type='str', required=True),
        securable=dict(type='str'),
        principal=dict(type='str', required=True),
        state=dict(type='str', default='grant', choices=['grant', 'revoke', 'deny']),
        with_grant_option=dict(type='bool', default=False),
    )
    module = AnsibleModule(
        argument_spec=argument_spec,
        supports_check_mode=True,
    )

    permission = module.params['permission']
    on_clause = module.params.get('securable')
    principal = module.params['principal']
    state = module.params['state']
    with_grant_option = module.params['with_grant_option']

    client = MSSQLClient(module)
    changed = False

    try:
        # Build T-SQL statement
        action = state.upper()
        sql = "%s %s" % (action, permission)
        if on_clause:
            sql += " ON %s" % on_clause
        if action == 'GRANT':
            sql += " TO [%s]" % principal
            if with_grant_option:
                sql += " WITH GRANT OPTION"
        elif action == 'DENY':
            sql += " TO [%s]" % principal
        elif action == 'REVOKE':
            sql += " FROM [%s]" % principal

        # Check current state
        current_state = check_permission(client, permission, principal, on_clause)
        desired_state = state.upper()
        # Map: grant->GRANT, deny->DENY, revoke->no entry
        state_map = {'GRANT': 'GRANT', 'GRANT_WITH_GRANT_OPTION': 'GRANT', 'DENY': 'DENY'}
        current_mapped = state_map.get(current_state)

        needs_change = False
        if desired_state == 'REVOKE' and current_state is not None:
            needs_change = True
        elif desired_state == 'GRANT' and current_mapped != 'GRANT':
            needs_change = True
        elif desired_state == 'DENY' and current_mapped != 'DENY':
            needs_change = True

        if needs_change:
            if not module.check_mode:
                client.execute_ddl(sql)
            changed = True

        module.exit_json(changed=changed, permission=permission, principal=principal, state=state)
    finally:
        client.close()


if __name__ == '__main__':
    main()
