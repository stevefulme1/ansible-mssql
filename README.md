# stevefulme1.mssql

Ansible Collection for Microsoft SQL Server -- database, login, user, role, AG, and backup management.

**Status: Pre-release (0.2.0). Under active development.**

## Overview

This collection provides modules for automating Microsoft SQL Server using the `pymssql` Python driver for T-SQL operations. All modules connect directly to SQL Server and execute real T-SQL against system views (`sys.databases`, `sys.server_principals`, `sys.database_principals`, etc.).

## Requirements

- ansible-core >= 2.16
- Python >= 3.11
- pymssql >= 2.2.0

## Installation

```bash
ansible-galaxy collection install stevefulme1.mssql
```

Or from source:

```bash
ansible-galaxy collection build
ansible-galaxy collection install stevefulme1-mssql-0.2.0.tar.gz
```

## Included Content

### Modules (12)

| Module | Description |
|--------|-------------|
| `mssql_database` | Create, alter, or drop databases |
| `mssql_database_info` | Gather database metadata from sys.databases |
| `mssql_login` | Create, alter, or drop server-level logins |
| `mssql_login_info` | Gather login metadata from sys.server_principals |
| `mssql_user` | Create, alter, or drop database-level users |
| `mssql_user_info` | Gather user metadata from sys.database_principals |
| `mssql_role_member` | Add/remove users from database roles |
| `mssql_permission` | GRANT, REVOKE, or DENY permissions |
| `mssql_ag` | Manage Always On Availability Groups |
| `mssql_ag_info` | Gather AG metadata from sys.availability_groups |
| `mssql_backup` | Backup databases (full, differential, log) |
| `mssql_query` | Execute arbitrary T-SQL and return results |

### Module Utils

| Utility | Description |
|---------|-------------|
| `mssql_client` | Shared pymssql connection wrapper (connect, execute_query, execute_ddl) |

### Doc Fragments

| Fragment | Description |
|----------|-------------|
| `mssql` | Shared connection parameters (login_host, login_port, login_user, login_password, database) |

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

## Usage Examples

```yaml
- name: Create a database
  stevefulme1.mssql.mssql_database:
    login_host: sqlserver.example.com
    login_user: sa
    login_password: "{{ vault_sa_password }}"
    name: myappdb
    recovery_model: SIMPLE

- name: Create a login and user
  hosts: localhost
  tasks:
    - stevefulme1.mssql.mssql_login:
        login_host: sqlserver.example.com
        login_user: sa
        login_password: "{{ vault_sa_password }}"
        name: app_svc
        password: "{{ vault_app_password }}"

    - stevefulme1.mssql.mssql_user:
        login_host: sqlserver.example.com
        login_user: sa
        login_password: "{{ vault_sa_password }}"
        database: myappdb
        name: app_svc
        login: app_svc

    - stevefulme1.mssql.mssql_role_member:
        login_host: sqlserver.example.com
        login_user: sa
        login_password: "{{ vault_sa_password }}"
        database: myappdb
        role: db_datareader
        member: app_svc

- name: Run a backup
  stevefulme1.mssql.mssql_backup:
    login_host: sqlserver.example.com
    login_user: sa
    login_password: "{{ vault_sa_password }}"
    name: myappdb
    path: /var/opt/mssql/backup/myappdb.bak
    compression: true
```

## License

GPL-3.0-or-later

## Community

- [Contributing](CONTRIBUTING.md) - How to contribute to this project
- [Code of Conduct](CODE_OF_CONDUCT.md) - Ansible Community Code of Conduct
- [Security Policy](SECURITY.md) - How to report security vulnerabilities
