#!/usr/bin/python
# -*- coding: utf-8 -*-
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r"""
---
module: mssql_role_member
short_description: Manage SQL Server database role membership
description:
  - Add or remove database users from database roles.
  - Uses C(sp_addrolemember) and C(sp_droprolemember) or C(ALTER ROLE) syntax.
version_added: "0.1.0"
options:
  role:
    description:
      - Name of the database role.
    type: str
    required: true
  member:
    description:
      - Name of the database user or role to add/remove.
    type: str
    required: true
  state:
    description:
      - Whether the member should be in the role.
    type: str
    choices: [present, absent]
    default: present
extends_documentation_fragment:
  - stevefulme1.mssql.mssql
author:
  - Steve Fulmer (@stevefulme1)
"""

EXAMPLES = r"""
- name: Add user to db_datareader role
  stevefulme1.mssql.mssql_role_member:
    login_host: sqlserver.example.com
    login_user: sa
    login_password: MyP@ssw0rd
    database: myappdb
    role: db_datareader
    member: app_user
    state: present

- name: Remove user from db_datawriter role
  stevefulme1.mssql.mssql_role_member:
    login_host: sqlserver.example.com
    login_user: sa
    login_password: MyP@ssw0rd
    database: myappdb
    role: db_datawriter
    member: app_user
    state: absent
"""

RETURN = r"""
role:
  description: The role name.
  returned: always
  type: str
member:
  description: The member name.
  returned: always
  type: str
state:
  description: The membership state.
  returned: always
  type: str
"""

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.stevefulme1.mssql.plugins.module_utils.mssql_client import (
    MSSQLClient,
    mssql_common_argument_spec,
)


def is_member(client, role, member):
    """Check if member is in the role via sys.database_role_members."""
    rows = client.execute_query(
        "SELECT 1 FROM sys.database_role_members rm "
        "JOIN sys.database_principals r ON rm.role_principal_id = r.principal_id "
        "JOIN sys.database_principals m ON rm.member_principal_id = m.principal_id "
        "WHERE r.name = %s AND m.name = %s",
        (role, member),
    )
    return len(rows) > 0


def main():
    argument_spec = mssql_common_argument_spec()
    argument_spec.update(
        role=dict(type='str', required=True),
        member=dict(type='str', required=True),
        state=dict(type='str', default='present', choices=['present', 'absent']),
    )
    module = AnsibleModule(
        argument_spec=argument_spec,
        supports_check_mode=True,
    )

    role = module.params['role']
    member = module.params['member']
    state = module.params['state']

    client = MSSQLClient(module)
    changed = False

    try:
        currently_member = is_member(client, role, member)

        if state == 'present' and not currently_member:
            if not module.check_mode:
                client.execute_ddl(
                    "ALTER ROLE [%s] ADD MEMBER [%s]" % (role, member)
                )
            changed = True
        elif state == 'absent' and currently_member:
            if not module.check_mode:
                client.execute_ddl(
                    "ALTER ROLE [%s] DROP MEMBER [%s]" % (role, member)
                )
            changed = True

        module.exit_json(changed=changed, role=role, member=member, state=state)
    finally:
        client.close()


if __name__ == '__main__':
    main()
