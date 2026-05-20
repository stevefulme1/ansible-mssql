# stevefulme1.mssql

Ansible Collection for Microsoft SQL Server -- database, login, user, role, AG, and backup management.

**Status: Pre-release (0.1.0). Under active development.**

## Overview

This collection will provide modules for automating Microsoft SQL Server using real database drivers:

- **On-premises** -- via `pymssql` or `pyodbc` Python drivers for T-SQL operations
- **Azure SQL** -- via Azure Resource Manager REST API

Placeholder roles are included for common operational workflows.

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
ansible-galaxy collection install stevefulme1-mssql-0.1.0.tar.gz
```

## Included Content

### Modules

No modules yet. Modules will use:

- `pymssql` or `pyodbc` for SQL Server operations via T-SQL
- Azure Resource Manager API for Azure SQL resources

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

## License

GPL-3.0-or-later

## Community

- [Contributing](CONTRIBUTING.md) - How to contribute to this project
- [Code of Conduct](CODE_OF_CONDUCT.md) - Ansible Community Code of Conduct
- [Security Policy](SECURITY.md) - How to report security vulnerabilities
