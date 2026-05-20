#!/usr/bin/python
# -*- coding: utf-8 -*-
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r"""
---
module: mssql_database_info
short_description: Gather information about SQL Server databases
description:
  - Returns information about databases on a Microsoft SQL Server instance.
  - Queries the C(sys.databases) system view.
version_added: "0.1.0"
options:
  name:
    description:
      - Name of a specific database to query.
      - If omitted, returns info for all databases.
    type: str
extends_documentation_fragment:
  - stevefulme1.mssql.mssql
author:
  - Steve Fulmer (@stevefulme1)
"""

EXAMPLES = r"""
- name: Get all database info
  stevefulme1.mssql.mssql_database_info:
    login_host: sqlserver.example.com
    login_user: sa
    login_password: MyP@ssw0rd
  register: db_info

- name: Get info for a specific database
  stevefulme1.mssql.mssql_database_info:
    login_host: sqlserver.example.com
    login_user: sa
    login_password: MyP@ssw0rd
    name: myappdb
  register: db_info
"""

RETURN = r"""
databases:
  description: List of database information dictionaries.
  returned: always
  type: list
  elements: dict
  contains:
    name:
      description: Database name.
      type: str
    database_id:
      description: Database ID.
      type: int
    state_desc:
      description: Database state.
      type: str
    recovery_model_desc:
      description: Recovery model.
      type: str
    collation_name:
      description: Collation.
      type: str
    compatibility_level:
      description: Compatibility level.
      type: int
    owner:
      description: Database owner login name.
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
            "SELECT d.name, d.database_id, d.state_desc, d.recovery_model_desc, "
            "d.collation_name, d.compatibility_level, SUSER_SNAME(d.owner_sid) AS owner "
            "FROM sys.databases d"
        )
        params = None
        if name:
            query += " WHERE d.name = %s"
            params = (name,)

        rows = client.execute_query(query, params)
        module.exit_json(changed=False, databases=rows)
    finally:
        client.close()


if __name__ == '__main__':
    main()
