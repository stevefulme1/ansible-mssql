# Changelog

## [0.2.0] - 2026-05-20

### Added
- `mssql_database` module -- CREATE/ALTER/DROP DATABASE via pymssql
- `mssql_database_info` module -- query sys.databases for database metadata
- `mssql_login` module -- CREATE/ALTER/DROP LOGIN (server-level auth)
- `mssql_login_info` module -- query sys.server_principals for login metadata
- `mssql_user` module -- CREATE/ALTER/DROP USER (database-level)
- `mssql_user_info` module -- query sys.database_principals for user metadata
- `mssql_role_member` module -- ALTER ROLE ADD/DROP MEMBER for role membership
- `mssql_permission` module -- GRANT/REVOKE/DENY permissions on securables
- `mssql_ag` module -- CREATE/ALTER/DROP Always On Availability Groups
- `mssql_ag_info` module -- query sys.availability_groups/replicas/databases
- `mssql_backup` module -- BACKUP DATABASE / BACKUP LOG with compression/checksum
- `mssql_query` module -- execute arbitrary T-SQL, return result sets
- `plugins/module_utils/mssql_client.py` -- shared pymssql connection wrapper
- `plugins/doc_fragments/mssql.py` -- shared connection parameter documentation

### Notes
- All modules use pymssql for real T-SQL operations against SQL Server
- All modules support check_mode
- All modules pass ansible-test sanity (validate-modules, pep8, pylint) and ansible-lint --strict

## [0.1.0] - 2026-05-20

### Removed
- Deleted 54 fabricated modules that used fake REST API endpoints instead of real pymssql/pyodbc SQL operations
- Deleted fabricated api_client.py module_utils (generic REST wrapper)
- Deleted fabricated mssql_inventory dynamic inventory plugin
- Deleted fabricated EDA event source plugins (agent_webhook, azure_activity_log, service_broker)
- Deleted associated unit tests for removed modules

### Retained
- 10 placeholder roles for common SQL Server operational workflows
- Collection scaffolding (LICENSE, CONTRIBUTING, CODE_OF_CONDUCT, SECURITY, MAINTAINERS)
- CI/CD workflow configuration

### Notes
- Version reset to 0.1.0 to reflect pre-release status
- Future modules will use pymssql/pyodbc for T-SQL operations and Azure RM API for Azure SQL
