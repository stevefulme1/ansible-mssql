#!/usr/bin/python
# -*- coding: utf-8 -*-
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r"""
---
module: mssql_database
short_description: Manage SQL Server databases
description:
  - Create, alter, or drop databases on a Microsoft SQL Server instance.
  - Uses pymssql to execute T-SQL statements against the server.
version_added: "0.1.0"
options:
  name:
    description:
      - Name of the database to manage.
    type: str
    required: true
  state:
    description:
      - Desired state of the database.
    type: str
    choices: [present, absent]
    default: present
  collation:
    description:
      - The collation for the database.
      - Only applied when creating a new database.
    type: str
  recovery_model:
    description:
      - The recovery model for the database.
    type: str
    choices: [FULL, SIMPLE, BULK_LOGGED]
  owner:
    description:
      - The database owner login name.
    type: str
extends_documentation_fragment:
  - stevefulme1.mssql.mssql
author:
  - Steve Fulmer (@stevefulme1)
"""

EXAMPLES = r"""
- name: Create a database
  stevefulme1.mssql.mssql_database:
    login_host: sqlserver.example.com
    login_user: sa
    login_password: MyP@ssw0rd
    name: myappdb
    state: present

- name: Create a database with specific collation and recovery model
  stevefulme1.mssql.mssql_database:
    login_host: sqlserver.example.com
    login_user: sa
    login_password: MyP@ssw0rd
    name: myappdb
    collation: SQL_Latin1_General_CP1_CI_AS
    recovery_model: SIMPLE
    state: present

- name: Drop a database
  stevefulme1.mssql.mssql_database:
    login_host: sqlserver.example.com
    login_user: sa
    login_password: MyP@ssw0rd
    name: myappdb
    state: absent
"""

RETURN = r"""
name:
  description: The name of the database.
  returned: always
  type: str
state:
  description: The state of the database.
  returned: always
  type: str
"""

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.stevefulme1.mssql.plugins.module_utils.mssql_client import (
    MSSQLClient,
    mssql_common_argument_spec,
)


def get_database(client, name):
    """Return database info from sys.databases or None."""
    rows = client.execute_query(
        "SELECT name, collation_name, recovery_model_desc, owner_sid "
        "FROM sys.databases WHERE name = %s",
        (name,),
    )
    return rows[0] if rows else None


def main():
    argument_spec = mssql_common_argument_spec()
    argument_spec.update(
        name=dict(type='str', required=True),
        state=dict(type='str', default='present', choices=['present', 'absent']),
        collation=dict(type='str'),
        recovery_model=dict(type='str', choices=['FULL', 'SIMPLE', 'BULK_LOGGED']),
        owner=dict(type='str'),
    )
    module = AnsibleModule(
        argument_spec=argument_spec,
        supports_check_mode=True,
    )

    name = module.params['name']
    state = module.params['state']
    collation = module.params.get('collation')
    recovery_model = module.params.get('recovery_model')
    owner = module.params.get('owner')

    client = MSSQLClient(module)
    changed = False

    try:
        current = get_database(client, name)

        if state == 'present':
            if not current:
                # Create database
                sql = "CREATE DATABASE [%s]" % name
                if collation:
                    sql += " COLLATE %s" % collation
                if not module.check_mode:
                    client.execute_ddl(sql)
                changed = True
            else:
                # Alter recovery model if needed
                if recovery_model and current.get('recovery_model_desc', '').upper() != recovery_model.upper():
                    if not module.check_mode:
                        client.execute_ddl(
                            "ALTER DATABASE [%s] SET RECOVERY %s" % (name, recovery_model)
                        )
                    changed = True
                # Alter owner if needed
                if owner:
                    current_owner = client.execute_scalar(
                        "SELECT SUSER_SNAME(owner_sid) FROM sys.databases WHERE name = %s",
                        (name,),
                    )
                    if current_owner and current_owner.lower() != owner.lower():
                        if not module.check_mode:
                            client.execute_ddl(
                                "ALTER AUTHORIZATION ON DATABASE::[%s] TO [%s]" % (name, owner)
                            )
                        changed = True

        elif state == 'absent':
            if current:
                if not module.check_mode:
                    client.execute_ddl(
                        "ALTER DATABASE [%s] SET SINGLE_USER WITH ROLLBACK IMMEDIATE" % name
                    )
                    client.execute_ddl("DROP DATABASE [%s]" % name)
                changed = True

        module.exit_json(changed=changed, name=name, state=state)
    finally:
        client.close()


if __name__ == '__main__':
    main()
