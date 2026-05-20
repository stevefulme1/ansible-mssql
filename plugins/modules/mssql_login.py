#!/usr/bin/python
# -*- coding: utf-8 -*-
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r"""
---
module: mssql_login
short_description: Manage SQL Server logins
description:
  - Create, alter, or drop server-level logins on a Microsoft SQL Server instance.
  - Manages SQL Server authentication logins via T-SQL.
version_added: "0.1.0"
options:
  name:
    description:
      - Name of the login to manage.
    type: str
    required: true
  password:
    description:
      - Password for the login.
      - Required when creating a new SQL login.
    type: str
  state:
    description:
      - Desired state of the login.
    type: str
    choices: [present, absent]
    default: present
  default_database:
    description:
      - Default database for the login.
    type: str
  default_language:
    description:
      - Default language for the login.
    type: str
  enabled:
    description:
      - Whether the login is enabled.
    type: bool
    default: true
  check_policy:
    description:
      - Whether to enforce password policy.
    type: bool
  check_expiration:
    description:
      - Whether to enforce password expiration policy.
    type: bool
extends_documentation_fragment:
  - stevefulme1.mssql.mssql
author:
  - Steve Fulmer (@stevefulme1)
"""

EXAMPLES = r"""
- name: Create a SQL login
  stevefulme1.mssql.mssql_login:
    login_host: sqlserver.example.com
    login_user: sa
    login_password: MyP@ssw0rd
    name: app_user
    password: AppUs3r!Pass
    state: present

- name: Disable a login
  stevefulme1.mssql.mssql_login:
    login_host: sqlserver.example.com
    login_user: sa
    login_password: MyP@ssw0rd
    name: app_user
    enabled: false

- name: Drop a login
  stevefulme1.mssql.mssql_login:
    login_host: sqlserver.example.com
    login_user: sa
    login_password: MyP@ssw0rd
    name: app_user
    state: absent
"""

RETURN = r"""
name:
  description: The login name.
  returned: always
  type: str
state:
  description: The state of the login.
  returned: always
  type: str
"""

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.stevefulme1.mssql.plugins.module_utils.mssql_client import (
    MSSQLClient,
    mssql_common_argument_spec,
)


def get_login(client, name):
    """Return login info from sys.server_principals or None."""
    rows = client.execute_query(
        "SELECT name, principal_id, type_desc, is_disabled, default_database_name, "
        "default_language_name, is_policy_checked, is_expiration_checked "
        "FROM sys.server_principals WHERE name = %s AND type IN ('S', 'U')",
        (name,),
    )
    return rows[0] if rows else None


def main():
    argument_spec = mssql_common_argument_spec()
    argument_spec.update(
        name=dict(type='str', required=True),
        password=dict(type='str', no_log=True),
        state=dict(type='str', default='present', choices=['present', 'absent']),
        default_database=dict(type='str'),
        default_language=dict(type='str'),
        enabled=dict(type='bool', default=True),
        check_policy=dict(type='bool'),
        check_expiration=dict(type='bool'),
    )
    module = AnsibleModule(
        argument_spec=argument_spec,
        supports_check_mode=True,
    )

    name = module.params['name']
    password = module.params.get('password')
    state = module.params['state']
    default_database = module.params.get('default_database')
    default_language = module.params.get('default_language')
    enabled = module.params['enabled']
    check_policy = module.params.get('check_policy')
    check_expiration = module.params.get('check_expiration')

    client = MSSQLClient(module)
    changed = False

    try:
        current = get_login(client, name)

        if state == 'present':
            if not current:
                if not password:
                    module.fail_json(msg="password is required when creating a new login")
                sql = "CREATE LOGIN [%s] WITH PASSWORD = '%s'" % (name, password)
                if default_database:
                    sql += ", DEFAULT_DATABASE = [%s]" % default_database
                if default_language:
                    sql += ", DEFAULT_LANGUAGE = [%s]" % default_language
                if check_policy is not None:
                    sql += ", CHECK_POLICY = %s" % ('ON' if check_policy else 'OFF')
                if check_expiration is not None:
                    sql += ", CHECK_EXPIRATION = %s" % ('ON' if check_expiration else 'OFF')
                if not module.check_mode:
                    client.execute_ddl(sql)
                if not enabled and not module.check_mode:
                    client.execute_ddl("ALTER LOGIN [%s] DISABLE" % name)
                changed = True
            else:
                # Alter existing login
                alter_parts = []
                if password:
                    alter_parts.append("PASSWORD = '%s'" % password)
                if default_database and current.get('default_database_name', '').lower() != default_database.lower():
                    alter_parts.append("DEFAULT_DATABASE = [%s]" % default_database)
                if default_language and current.get('default_language_name', '').lower() != default_language.lower():
                    alter_parts.append("DEFAULT_LANGUAGE = [%s]" % default_language)
                if check_policy is not None:
                    current_val = bool(current.get('is_policy_checked'))
                    if current_val != check_policy:
                        alter_parts.append("CHECK_POLICY = %s" % ('ON' if check_policy else 'OFF'))
                if check_expiration is not None:
                    current_val = bool(current.get('is_expiration_checked'))
                    if current_val != check_expiration:
                        alter_parts.append("CHECK_EXPIRATION = %s" % ('ON' if check_expiration else 'OFF'))

                if alter_parts:
                    sql = "ALTER LOGIN [%s] WITH %s" % (name, ", ".join(alter_parts))
                    if not module.check_mode:
                        client.execute_ddl(sql)
                    changed = True

                # Handle enable/disable
                is_disabled = bool(current.get('is_disabled'))
                if enabled and is_disabled:
                    if not module.check_mode:
                        client.execute_ddl("ALTER LOGIN [%s] ENABLE" % name)
                    changed = True
                elif not enabled and not is_disabled:
                    if not module.check_mode:
                        client.execute_ddl("ALTER LOGIN [%s] DISABLE" % name)
                    changed = True

        elif state == 'absent':
            if current:
                if not module.check_mode:
                    client.execute_ddl("DROP LOGIN [%s]" % name)
                changed = True

        module.exit_json(changed=changed, name=name, state=state)
    finally:
        client.close()


if __name__ == '__main__':
    main()
