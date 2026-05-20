# Changelog

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
