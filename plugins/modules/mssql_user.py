#!/usr/bin/python
# -*- coding: utf-8 -*-
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r"""
---
module: mssql_user
short_description: Manage SQL Server database users
description:
  - Create, alter, or drop database-level users on a Microsoft SQL Server instance.
  - Maps logins to database users via T-SQL.
version_added: "0.1.0"
options:
  name:
    description:
      - Name of the database user to manage.
    type: str
    required: true
  login:
    description:
      - The server login to map this user to.
      - Required when creating a new user (unless creating a user without login).
    type: str
  state:
    description:
      - Desired state of the user.
    type: str
    choices: [present, absent]
    default: present
  default_schema:
    description:
      - Default schema for the user.
    type: str
extends_documentation_fragment:
  - stevefulme1.mssql.mssql
author:
  - Steve Fulmer (@stevefulme1)
"""

EXAMPLES = r"""
- name: Create a database user mapped to a login
  stevefulme1.mssql.mssql_user:
    login_host: sqlserver.example.com
    login_user: sa
    login_password: MyP@ssw0rd
    database: myappdb
    name: app_user
    login: app_login
    state: present

- name: Drop a database user
  stevefulme1.mssql.mssql_user:
    login_host: sqlserver.example.com
    login_user: sa
    login_password: MyP@ssw0rd
    database: myappdb
    name: app_user
    state: absent
"""

RETURN = r"""
name:
  description: The user name.
  returned: always
  type: str
state:
  description: The state of the user.
  returned: always
  type: str
"""

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.stevefulme1.mssql.plugins.module_utils.mssql_client import (
    MSSQLClient,
    mssql_common_argument_spec,
)


def get_user(client, name):
    """Return user info from sys.database_principals or None."""
    rows = client.execute_query(
        "SELECT name, principal_id, type_desc, default_schema_name "
        "FROM sys.database_principals WHERE name = %s AND type IN ('S', 'U')",
        (name,),
    )
    return rows[0] if rows else None


def main():
    argument_spec = mssql_common_argument_spec()
    argument_spec.update(
        name=dict(type='str', required=True),
        login=dict(type='str'),
        state=dict(type='str', default='present', choices=['present', 'absent']),
        default_schema=dict(type='str'),
    )
    module = AnsibleModule(
        argument_spec=argument_spec,
        supports_check_mode=True,
    )

    name = module.params['name']
    login = module.params.get('login')
    state = module.params['state']
    default_schema = module.params.get('default_schema')

    client = MSSQLClient(module)
    changed = False

    try:
        current = get_user(client, name)

        if state == 'present':
            if not current:
                sql = "CREATE USER [%s]" % name
                if login:
                    sql += " FOR LOGIN [%s]" % login
                if default_schema:
                    sql += " WITH DEFAULT_SCHEMA = [%s]" % default_schema
                if not module.check_mode:
                    client.execute_ddl(sql)
                changed = True
            else:
                # Alter default schema if needed
                if default_schema:
                    current_schema = current.get('default_schema_name', '')
                    if current_schema and current_schema.lower() != default_schema.lower():
                        if not module.check_mode:
                            client.execute_ddl(
                                "ALTER USER [%s] WITH DEFAULT_SCHEMA = [%s]" % (name, default_schema)
                            )
                        changed = True

        elif state == 'absent':
            if current:
                if not module.check_mode:
                    client.execute_ddl("DROP USER [%s]" % name)
                changed = True

        module.exit_json(changed=changed, name=name, state=state)
    finally:
        client.close()


if __name__ == '__main__':
    main()
