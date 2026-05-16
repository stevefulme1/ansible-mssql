#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright 2026 Steve Fulmer
# Apache-2.0 (see LICENSE)
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

"""mssql_agent_schedule module."""

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r"""
---
module: mssql_agent_schedule
short_description: Manage SQL Server Agent schedules
description:
    - Manage SQL Server Agent schedules.
version_added: "1.0.0"
author:
    - Steve Fulmer (@stevefulme1)
options:
    state:
        description: Desired state of the resource.
        type: str
        default: present
        choices: [present, absent]
    host:
        description: API host address.
        type: str
        required: true
    schedule_name:
        description: Unique identifier of the agent schedule.
        type: str
    name:
        description: Display name.
        type: str
    username:
        description: Authentication username.
        type: str
    password:
        description: Authentication password.
        type: str
    api_key:
        description: API key for authentication.
        type: str
    validate_certs:
        description: Validate SSL certificates.
        type: bool
        default: true
"""

EXAMPLES = r"""
- name: Create a agent schedule
  stevefulme1.mssql.mssql_agent_schedule:
    host: api.example.com
    name: my-agent-schedule
    state: present

- name: Delete a agent schedule
  stevefulme1.mssql.mssql_agent_schedule:
    host: api.example.com
    schedule_name: "example-id"
    state: absent
"""

RETURN = r"""
agent_schedule:
    description: Resource details.
    returned: on success
    type: dict
"""

from ansible.module_utils.basic import AnsibleModule

try:
    from ansible_collections.stevefulme1.mssql.plugins.module_utils.api_client import ApiClient
    HAS_CLIENT = True
except ImportError:
    HAS_CLIENT = False


def main():
    module = AnsibleModule(
        argument_spec=dict(
            state=dict(type="str", default="present", choices=["present", "absent"]),
            schedule_name=dict(type="str"),
            name=dict(type="str"),
            host=dict(type="str", required=True),
            username=dict(type="str"),
            password=dict(type="str", no_log=True),
            api_key=dict(type="str", no_log=True),
            validate_certs=dict(type="bool", default=True),
        ),
        supports_check_mode=True,
        required_if=[("state", "absent", ("schedule_name",))],
    )

    if not HAS_CLIENT:
        module.fail_json(msg="Required Python libraries not found.")

    client = ApiClient(module)
    state = module.params["state"]
    resource_id = module.params.get("schedule_name")

    if state == "present":
        if resource_id:
            result = client.update("agent_schedule", resource_id, module.params)
        else:
            if module.check_mode:
                module.exit_json(changed=True)
            result = client.create("agent_schedule", module.params)
        module.exit_json(changed=True, agent_schedule=result)
    else:
        if module.check_mode:
            module.exit_json(changed=True)
        client.delete("agent_schedule", resource_id)
        module.exit_json(changed=True)


if __name__ == "__main__":
    main()
