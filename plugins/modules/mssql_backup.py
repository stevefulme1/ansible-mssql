#!/usr/bin/python
# -*- coding: utf-8 -*-
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r"""
---
module: mssql_backup
short_description: Backup SQL Server databases
description:
  - Execute BACKUP DATABASE or BACKUP LOG against a SQL Server instance.
  - Supports full, differential, and log backups.
version_added: "0.1.0"
options:
  name:
    description:
      - Name of the database to back up.
    type: str
    required: true
  path:
    description:
      - File path for the backup file on the SQL Server host.
    type: str
    required: true
  type:
    description:
      - Type of backup to perform.
    type: str
    choices: [full, differential, log]
    default: full
  compression:
    description:
      - Whether to compress the backup.
    type: bool
    default: false
  copy_only:
    description:
      - Whether this is a copy-only backup.
    type: bool
    default: false
  description:
    description:
      - Description for the backup set.
    type: str
  checksum:
    description:
      - Whether to include a checksum in the backup.
    type: bool
    default: false
extends_documentation_fragment:
  - stevefulme1.mssql.mssql
author:
  - Steve Fulmer (@stevefulme1)
"""

EXAMPLES = r"""
- name: Full database backup
  stevefulme1.mssql.mssql_backup:
    login_host: sqlserver.example.com
    login_user: sa
    login_password: MyP@ssw0rd
    name: myappdb
    path: /var/opt/mssql/backup/myappdb_full.bak
    type: full

- name: Transaction log backup with compression
  stevefulme1.mssql.mssql_backup:
    login_host: sqlserver.example.com
    login_user: sa
    login_password: MyP@ssw0rd
    name: myappdb
    path: /var/opt/mssql/backup/myappdb_log.trn
    type: log
    compression: true

- name: Differential backup with checksum
  stevefulme1.mssql.mssql_backup:
    login_host: sqlserver.example.com
    login_user: sa
    login_password: MyP@ssw0rd
    name: myappdb
    path: /var/opt/mssql/backup/myappdb_diff.bak
    type: differential
    checksum: true
"""

RETURN = r"""
name:
  description: The database that was backed up.
  returned: always
  type: str
path:
  description: The backup file path.
  returned: always
  type: str
type:
  description: The backup type performed.
  returned: always
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
        name=dict(type='str', required=True),
        path=dict(type='str', required=True),
        type=dict(type='str', default='full', choices=['full', 'differential', 'log']),
        compression=dict(type='bool', default=False),
        copy_only=dict(type='bool', default=False),
        description=dict(type='str'),
        checksum=dict(type='bool', default=False),
    )
    module = AnsibleModule(
        argument_spec=argument_spec,
        supports_check_mode=True,
    )

    name = module.params['name']
    path = module.params['path']
    backup_type = module.params['type']
    compression = module.params['compression']
    copy_only = module.params['copy_only']
    description = module.params.get('description')
    checksum = module.params['checksum']

    client = MSSQLClient(module)

    try:
        if backup_type == 'log':
            sql = "BACKUP LOG [%s] TO DISK = N'%s'" % (name, path)
        else:
            sql = "BACKUP DATABASE [%s] TO DISK = N'%s'" % (name, path)

        with_clauses = []
        if backup_type == 'differential':
            with_clauses.append("DIFFERENTIAL")
        if copy_only:
            with_clauses.append("COPY_ONLY")
        if compression:
            with_clauses.append("COMPRESSION")
        if checksum:
            with_clauses.append("CHECKSUM")
        if description:
            with_clauses.append("DESCRIPTION = N'%s'" % description)

        if with_clauses:
            sql += " WITH %s" % ", ".join(with_clauses)

        if not module.check_mode:
            client.execute_ddl(sql)

        module.exit_json(changed=True, name=name, path=path, type=backup_type)
    finally:
        client.close()


if __name__ == '__main__':
    main()
