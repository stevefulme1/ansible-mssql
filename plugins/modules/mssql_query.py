#!/usr/bin/python
# -*- coding: utf-8 -*-
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r"""
---
module: mssql_query
short_description: Execute arbitrary T-SQL queries
description:
  - Execute one or more T-SQL statements against a SQL Server instance.
  - Returns query results for SELECT statements.
  - This is an action module that always reports changed=true for non-SELECT queries.
version_added: "0.1.0"
options:
  query:
    description:
      - The T-SQL query or statement to execute.
      - Multiple statements can be separated by semicolons.
    type: str
    required: true
  params:
    description:
      - Parameters to pass to the query as a list.
      - Values are substituted for C(%s) placeholders in order.
    type: list
    elements: raw
  autocommit:
    description:
      - Whether to autocommit each statement.
    type: bool
    default: true
extends_documentation_fragment:
  - stevefulme1.mssql.mssql
author:
  - Steve Fulmer (@stevefulme1)
"""

EXAMPLES = r"""
- name: Run a SELECT query
  stevefulme1.mssql.mssql_query:
    login_host: sqlserver.example.com
    login_user: sa
    login_password: MyP@ssw0rd
    database: myappdb
    query: "SELECT name, create_date FROM sys.tables"
  register: result

- name: Run a parameterized query
  stevefulme1.mssql.mssql_query:
    login_host: sqlserver.example.com
    login_user: sa
    login_password: MyP@ssw0rd
    database: myappdb
    query: "SELECT * FROM users WHERE department = %s"
    params:
      - Engineering
  register: result

- name: Execute a DDL statement
  stevefulme1.mssql.mssql_query:
    login_host: sqlserver.example.com
    login_user: sa
    login_password: MyP@ssw0rd
    database: myappdb
    query: "CREATE TABLE test_table (id INT PRIMARY KEY, name NVARCHAR(100))"
"""

RETURN = r"""
results:
  description: List of rows returned by the query (for SELECT statements).
  returned: when query returns results
  type: list
  elements: dict
rowcount:
  description: Number of rows affected by the query.
  returned: always
  type: int
query:
  description: The query that was executed.
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
        query=dict(type='str', required=True),
        params=dict(type='list', elements='raw'),
        autocommit=dict(type='bool', default=True),
    )
    module = AnsibleModule(
        argument_spec=argument_spec,
        supports_check_mode=True,
    )

    query = module.params['query']
    params = module.params.get('params')
    autocommit = module.params['autocommit']

    if module.check_mode:
        module.exit_json(changed=True, query=query, results=[], rowcount=0)

    client = MSSQLClient(module)

    try:
        cursor = client.cursor(as_dict=True)
        try:
            if params:
                cursor.execute(query, tuple(params))
            else:
                cursor.execute(query)
        except Exception as e:
            module.fail_json(msg="Query execution failed: %s" % str(e))

        # Determine if this was a SELECT-like query
        results = []
        rowcount = cursor.rowcount if cursor.rowcount >= 0 else 0
        is_select = query.strip().upper().startswith('SELECT') or query.strip().upper().startswith('WITH')

        if is_select:
            try:
                results = cursor.fetchall()
                # Convert non-serializable types to strings
                for row in results:
                    for key, value in row.items():
                        if not isinstance(value, (str, int, float, bool, type(None))):
                            row[key] = str(value)
                rowcount = len(results)
            except Exception:
                pass
            changed = False
        else:
            if autocommit:
                client.conn.commit()
            changed = True

        module.exit_json(
            changed=changed,
            query=query,
            results=results,
            rowcount=rowcount,
        )
    finally:
        client.close()


if __name__ == '__main__':
    main()
