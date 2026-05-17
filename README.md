# stevefulme1.mssql

Ansible Collection for Microsoft SQL Server -- database/login/user/role management, AG, TDE, Agent jobs, Azure SQL, and EDA event-driven automation.

## Overview

This collection provides **55 modules** for automating Microsoft SQL Server infrastructure (on-premises and Azure SQL), along with 10 operational roles, a dynamic inventory plugin, and CI/CD workflows.

## Requirements

- ansible-core >= 2.16
- Python >= 3.11

## Installation

```bash
ansible-galaxy collection install stevefulme1.mssql
```

Or from source:

```bash
ansible-galaxy collection build
ansible-galaxy collection install stevefulme1-mssql-2.0.0.tar.gz
```

## Included Content

### Modules (55)

CRUD and info modules covering:

- **Databases** -- create, alter, drop, backup, restore
- **Security** -- logins, users, roles, permissions, TDE
- **Availability** -- Always On AG, failover, replicas
- **Agent** -- jobs, schedules, operators, alerts
- **Azure SQL** -- managed instances, elastic pools, firewall rules
- **Maintenance** -- index rebuild, statistics update, integrity checks
- **Monitoring** -- DMV queries, performance counters, wait stats

### Roles (10)

| Role | Description |
|------|-------------|
| `mssql_ag_setup` | Configure Always On Availability Groups |
| `mssql_azure_migration` | Migrate to Azure SQL |
| `mssql_backup_restore` | Backup and restore operations |
| `mssql_disaster_recovery` | DR configuration and failover |
| `mssql_maintenance` | Index and statistics maintenance |
| `mssql_monitoring` | Performance monitoring setup |
| `mssql_patching` | SQL Server patching procedures |
| `mssql_performance_tuning` | Performance optimization |
| `mssql_security_hardening` | Security baseline configuration |
| `mssql_user_management` | User and role management |

### Inventory Plugin

- `mssql_inventory` -- Dynamic inventory from SQL Server instances

## Usage

```yaml
- name: Create a database
  stevefulme1.mssql.mssql_database:
    host: "{{ mssql_host }}"
    username: "{{ mssql_user }}"
    password: "{{ mssql_pass }}"
    name: myapp_db
    recovery_model: FULL
    state: present
```

## License

Apache-2.0
