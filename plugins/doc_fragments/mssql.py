# -*- coding: utf-8 -*-
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import absolute_import, division, print_function
__metaclass__ = type


class ModuleDocFragment(object):
    DOCUMENTATION = r"""
options:
  login_host:
    description:
      - The hostname or IP address of the SQL Server instance.
    type: str
    default: localhost
  login_port:
    description:
      - The TCP port of the SQL Server instance.
    type: int
    default: 1433
  login_user:
    description:
      - The username to authenticate with.
    type: str
    required: true
  login_password:
    description:
      - The password to authenticate with.
    type: str
    required: true
  database:
    description:
      - The default database context for the connection.
    type: str
    default: master
"""
