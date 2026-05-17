"""Filter Microsoft SQL Server alerts by severity and database."""

DOCUMENTATION = r"""
---
event_filter: alert_filter
short_description: Filter MSSQL alerts by severity and database
description:
  - Filters SQL Server Agent alerts, Azure Activity Log events, and
    Service Broker messages by severity level and database name.
  - Supports severity values matching SQL Server error severity levels.
version_added: "1.0.0"
author: Steve Fulmer (@stevefulme1)
options:
  min_severity:
    description:
      - Minimum severity level (1-25) to pass through.
      - SQL Server uses 1-10 for informational, 11-16 for user errors,
        17-25 for system/fatal errors.
    type: int
    default: 11
  databases:
    description:
      - List of database names to include.
      - Empty list means all databases are included.
    type: list
    elements: str
    default: []
  exclude_system_dbs:
    description: Whether to exclude system databases (master, msdb, tempdb, model).
    type: bool
    default: true
  severity_key:
    description: Key in the event payload that contains the severity value.
    type: str
    default: severity
  database_key:
    description: Key in the event payload that contains the database name.
    type: str
    default: database_name
"""

EXAMPLES = r"""
- stevefulme1.mssql.alert_filter:
    min_severity: 16
    databases: [production, staging]
    exclude_system_dbs: true
"""

SYSTEM_DBS = {"master", "msdb", "tempdb", "model", "resource"}


def main(event, min_severity=11, databases=None, exclude_system_dbs=True,
         severity_key="severity", database_key="database_name"):
    """Filter MSSQL alerts by severity and database."""
    if not isinstance(event, dict):
        return event
    if databases is None:
        databases = []

    payload = event.get("payload", event)

    # Try to get severity as int
    try:
        sev = int(payload.get(severity_key, 0))
    except (ValueError, TypeError):
        sev = 0

    if sev < min_severity:
        return None

    db_name = str(payload.get(database_key, "")).lower()

    if exclude_system_dbs and db_name in SYSTEM_DBS:
        return None

    if databases and db_name not in [d.lower() for d in databases]:
        return None

    return event
