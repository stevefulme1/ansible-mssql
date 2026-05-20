#!/usr/bin/python
# -*- coding: utf-8 -*-
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r"""
---
module: mssql_ag
short_description: Manage SQL Server Always On Availability Groups
description:
  - Create, alter, or drop Always On Availability Groups.
  - Add or remove replicas and databases from an availability group.
  - Uses T-SQL against C(sys.availability_groups) and C(sys.availability_replicas).
version_added: "0.1.0"
options:
  name:
    description:
      - Name of the availability group.
    type: str
    required: true
  state:
    description:
      - Desired state of the availability group.
    type: str
    choices: [present, absent]
    default: present
  automated_backup_preference:
    description:
      - Backup preference for the AG.
    type: str
    choices: [PRIMARY, SECONDARY_ONLY, SECONDARY, NONE]
  failure_condition_level:
    description:
      - Failure condition level (1-5).
    type: int
    choices: [1, 2, 3, 4, 5]
  health_check_timeout:
    description:
      - Health check timeout in milliseconds.
    type: int
  db_failover:
    description:
      - Whether database-level health detection is enabled.
    type: bool
  replicas:
    description:
      - List of replica definitions to add.
      - Each item must have C(server_name) and optionally C(endpoint_url),
        C(availability_mode), C(failover_mode), C(seeding_mode).
    type: list
    elements: dict
    suboptions:
      server_name:
        description: The server instance name for this replica.
        type: str
        required: true
      endpoint_url:
        description: The database mirroring endpoint URL.
        type: str
      availability_mode:
        description: Availability mode.
        type: str
        choices: [SYNCHRONOUS_COMMIT, ASYNCHRONOUS_COMMIT]
        default: ASYNCHRONOUS_COMMIT
      failover_mode:
        description: Failover mode.
        type: str
        choices: [AUTOMATIC, MANUAL]
        default: MANUAL
      seeding_mode:
        description: Seeding mode.
        type: str
        choices: [AUTOMATIC, MANUAL]
        default: MANUAL
  databases:
    description:
      - List of database names to add to the availability group.
    type: list
    elements: str
extends_documentation_fragment:
  - stevefulme1.mssql.mssql
author:
  - Steve Fulmer (@stevefulme1)
"""

EXAMPLES = r"""
- name: Create an availability group with one replica
  stevefulme1.mssql.mssql_ag:
    login_host: sqlserver1.example.com
    login_user: sa
    login_password: MyP@ssw0rd
    name: MyAG
    replicas:
      - server_name: sqlserver1
        endpoint_url: "TCP://sqlserver1.example.com:5022"
        availability_mode: SYNCHRONOUS_COMMIT
        failover_mode: AUTOMATIC
        seeding_mode: AUTOMATIC
    state: present

- name: Drop an availability group
  stevefulme1.mssql.mssql_ag:
    login_host: sqlserver1.example.com
    login_user: sa
    login_password: MyP@ssw0rd
    name: MyAG
    state: absent
"""

RETURN = r"""
name:
  description: The availability group name.
  returned: always
  type: str
state:
  description: The state of the availability group.
  returned: always
  type: str
"""

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.stevefulme1.mssql.plugins.module_utils.mssql_client import (
    MSSQLClient,
    mssql_common_argument_spec,
)


def get_ag(client, name):
    """Return AG info from sys.availability_groups or None."""
    rows = client.execute_query(
        "SELECT group_id, name, automated_backup_preference_desc, "
        "failure_condition_level, health_check_timeout, db_failover "
        "FROM sys.availability_groups WHERE name = %s",
        (name,),
    )
    return rows[0] if rows else None


def main():
    replica_spec = dict(
        server_name=dict(type='str', required=True),
        endpoint_url=dict(type='str'),
        availability_mode=dict(
            type='str', default='ASYNCHRONOUS_COMMIT',
            choices=['SYNCHRONOUS_COMMIT', 'ASYNCHRONOUS_COMMIT'],
        ),
        failover_mode=dict(type='str', default='MANUAL', choices=['AUTOMATIC', 'MANUAL']),
        seeding_mode=dict(type='str', default='MANUAL', choices=['AUTOMATIC', 'MANUAL']),
    )

    argument_spec = mssql_common_argument_spec()
    argument_spec.update(
        name=dict(type='str', required=True),
        state=dict(type='str', default='present', choices=['present', 'absent']),
        automated_backup_preference=dict(
            type='str', choices=['PRIMARY', 'SECONDARY_ONLY', 'SECONDARY', 'NONE'],
        ),
        failure_condition_level=dict(type='int', choices=[1, 2, 3, 4, 5]),
        health_check_timeout=dict(type='int'),
        db_failover=dict(type='bool'),
        replicas=dict(type='list', elements='dict', options=replica_spec),
        databases=dict(type='list', elements='str'),
    )
    module = AnsibleModule(
        argument_spec=argument_spec,
        supports_check_mode=True,
    )

    name = module.params['name']
    state = module.params['state']
    replicas = module.params.get('replicas') or []
    databases = module.params.get('databases') or []
    automated_backup_preference = module.params.get('automated_backup_preference')
    failure_condition_level = module.params.get('failure_condition_level')
    health_check_timeout = module.params.get('health_check_timeout')
    db_failover = module.params.get('db_failover')

    client = MSSQLClient(module)
    changed = False

    try:
        current = get_ag(client, name)

        if state == 'present':
            if not current:
                # Build CREATE AVAILABILITY GROUP statement
                if not replicas:
                    module.fail_json(msg="At least one replica is required to create an availability group")

                replica_clauses = []
                for r in replicas:
                    clause = "N'%s'" % r['server_name']
                    clause += " WITH ("
                    parts = []
                    if r.get('endpoint_url'):
                        parts.append("ENDPOINT_URL = N'%s'" % r['endpoint_url'])
                    parts.append("AVAILABILITY_MODE = %s" % r.get('availability_mode', 'ASYNCHRONOUS_COMMIT'))
                    parts.append("FAILOVER_MODE = %s" % r.get('failover_mode', 'MANUAL'))
                    parts.append("SEEDING_MODE = %s" % r.get('seeding_mode', 'MANUAL'))
                    clause += ", ".join(parts) + ")"
                    replica_clauses.append(clause)

                sql = "CREATE AVAILABILITY GROUP [%s] FOR" % name

                if databases:
                    db_clauses = ["DATABASE [%s]" % db for db in databases]
                    sql += " %s" % ", ".join(db_clauses)

                sql += " REPLICA ON %s" % ",\n".join(replica_clauses)

                if not module.check_mode:
                    client.execute_ddl(sql)
                changed = True
            else:
                # Alter existing AG settings
                alter_parts = []
                if automated_backup_preference:
                    current_val = current.get('automated_backup_preference_desc', '').upper()
                    if current_val != automated_backup_preference.upper():
                        alter_parts.append(
                            "AUTOMATED_BACKUP_PREFERENCE = %s" % automated_backup_preference
                        )
                if failure_condition_level is not None:
                    if current.get('failure_condition_level') != failure_condition_level:
                        alter_parts.append(
                            "FAILURE_CONDITION_LEVEL = %d" % failure_condition_level
                        )
                if health_check_timeout is not None:
                    if current.get('health_check_timeout') != health_check_timeout:
                        alter_parts.append(
                            "HEALTH_CHECK_TIMEOUT = %d" % health_check_timeout
                        )
                if db_failover is not None:
                    current_val = bool(current.get('db_failover'))
                    if current_val != db_failover:
                        alter_parts.append(
                            "DB_FAILOVER = %s" % ('ON' if db_failover else 'OFF')
                        )

                if alter_parts:
                    sql = "ALTER AVAILABILITY GROUP [%s] SET (%s)" % (
                        name, ", ".join(alter_parts)
                    )
                    if not module.check_mode:
                        client.execute_ddl(sql)
                    changed = True

                # Add databases if specified
                if databases:
                    current_dbs = client.execute_query(
                        "SELECT database_name FROM sys.availability_databases_cluster "
                        "WHERE group_id = %s",
                        (current['group_id'],),
                    )
                    current_db_names = {r['database_name'].lower() for r in current_dbs}
                    for db in databases:
                        if db.lower() not in current_db_names:
                            if not module.check_mode:
                                client.execute_ddl(
                                    "ALTER AVAILABILITY GROUP [%s] ADD DATABASE [%s]" % (name, db)
                                )
                            changed = True

        elif state == 'absent':
            if current:
                if not module.check_mode:
                    client.execute_ddl("DROP AVAILABILITY GROUP [%s]" % name)
                changed = True

        module.exit_json(changed=changed, name=name, state=state)
    finally:
        client.close()


if __name__ == '__main__':
    main()
