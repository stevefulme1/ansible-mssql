# -*- coding: utf-8 -*-
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

"""Shared pymssql wrapper for stevefulme1.mssql collection modules."""

from __future__ import absolute_import, division, print_function
__metaclass__ = type

try:
    import pymssql
    HAS_PYMSSQL = True
    PYMSSQL_IMPORT_ERROR = None
except ImportError as e:
    HAS_PYMSSQL = False
    PYMSSQL_IMPORT_ERROR = str(e)


def mssql_common_argument_spec():
    """Return the argument spec shared by all mssql modules."""
    return dict(
        login_host=dict(type='str', default='localhost'),
        login_port=dict(type='int', default=1433),
        login_user=dict(type='str', required=True),
        login_password=dict(type='str', required=True, no_log=True),
        database=dict(type='str', default='master'),
    )


class MSSQLClient(object):
    """Thin wrapper around pymssql for Ansible modules."""

    def __init__(self, module):
        self.module = module
        if not HAS_PYMSSQL:
            module.fail_json(
                msg="The pymssql Python package is required. Install it with: pip install pymssql",
                exception=PYMSSQL_IMPORT_ERROR,
            )
        try:
            self.conn = pymssql.connect(
                server=module.params['login_host'],
                port=module.params['login_port'],
                user=module.params['login_user'],
                password=module.params['login_password'],
                database=module.params.get('database', 'master'),
                autocommit=False,
            )
        except pymssql.Error as e:
            module.fail_json(msg="Failed to connect to SQL Server: %s" % str(e))

    def cursor(self, as_dict=True):
        """Return a new cursor."""
        return self.conn.cursor(as_dict=as_dict)

    def execute_query(self, query, params=None):
        """Execute a SELECT and return all rows."""
        cursor = self.cursor(as_dict=True)
        try:
            cursor.execute(query, params)
            return cursor.fetchall()
        except pymssql.Error as e:
            self.module.fail_json(msg="Query failed: %s" % str(e))

    def execute_ddl(self, query, params=None, autocommit=True):
        """Execute a DDL/DML statement."""
        cursor = self.cursor(as_dict=False)
        try:
            cursor.execute(query, params)
            if autocommit:
                self.conn.commit()
        except pymssql.Error as e:
            self.conn.rollback()
            self.module.fail_json(msg="DDL execution failed: %s" % str(e))

    def execute_scalar(self, query, params=None):
        """Execute a query and return the first column of the first row."""
        cursor = self.cursor(as_dict=False)
        try:
            cursor.execute(query, params)
            row = cursor.fetchone()
            if row:
                return row[0]
            return None
        except pymssql.Error as e:
            self.module.fail_json(msg="Scalar query failed: %s" % str(e))

    def close(self):
        """Close the connection."""
        if self.conn:
            self.conn.close()
