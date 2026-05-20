#!/usr/bin/python
# -*- coding: utf-8 -*-
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r"""
---
module: mssql_ag_info
short_description: Gather information about SQL Server Always On Availability Groups
description:
  - Returns information about Always On Availability Groups.
  - Queries C(sys.availability_groups), C(sys.availability_replicas),
    and C(sys.availability_databases_cluster).
version_added: "0.1.0"
options:
  name:
    description:
      - Name of a specific availability group to query.
      - If omitted, returns info for all availability groups.
    type: str
extends_documentation_fragment:
  - stevefulme1.mssql.mssql
author:
  - Steve Fulmer (@stevefulme1)
"""

EXAMPLES = r"""
- name: Get all availability group info
  stevefulme1.mssql.mssql_ag_info:
    login_host: sqlserver.example.com
    login_user: sa
    login_password: MyP@ssw0rd
  register: ag_info

- name: Get info for a specific availability group
  stevefulme1.mssql.mssql_ag_info:
    login_host: sqlserver.example.com
    login_user: sa
    login_password: MyP@ssw0rd
    name: MyAG
  register: ag_info
"""

RETURN = r"""
availability_groups:
  description: List of availability group information dictionaries.
  returned: always
  type: list
  elements: dict
  contains:
    name:
      description: Availability group name.
      type: str
    group_id:
      description: Availability group ID.
      type: str
    automated_backup_preference_desc:
      description: Backup preference.
      type: str
    failure_condition_level:
      description: Failure condition level.
      type: int
    replicas:
      description: List of replicas in the AG.
      type: list
    databases:
      description: List of databases in the AG.
      type: list
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
            "SELECT ag.group_id, ag.name, ag.automated_backup_preference_desc, "
            "ag.failure_condition_level, ag.health_check_timeout "
            "FROM sys.availability_groups ag"
        )
        params = None
        if name:
            query += " WHERE ag.name = %s"
            params = (name,)

        ags = client.execute_query(query, params)

        for ag in ags:
            # Convert group_id to string for JSON
            if ag.get('group_id'):
                ag['group_id'] = str(ag['group_id'])

            # Fetch replicas
            replicas = client.execute_query(
                "SELECT replica_server_name, endpoint_url, "
                "availability_mode_desc, failover_mode_desc, seeding_mode_desc "
                "FROM sys.availability_replicas WHERE group_id = %s",
                (ag['group_id'],),
            )
            ag['replicas'] = replicas

            # Fetch databases
            databases = client.execute_query(
                "SELECT database_name FROM sys.availability_databases_cluster "
                "WHERE group_id = %s",
                (ag['group_id'],),
            )
            ag['databases'] = [d['database_name'] for d in databases]

        module.exit_json(changed=False, availability_groups=ags)
    finally:
        client.close()


if __name__ == '__main__':
    main()
