# Changelog

## [2.0.1] - 2026-05-18

### Security
- Prevent credential leak in API request bodies: connection params (password,
  api_key, username, host, validate_certs) are now stripped before POST/PUT
- Added request timeout (30 s) to all HTTP methods to prevent hung connections
- Hardened .gitignore against accidental credential commits

## [2.0.0] - 2026-05-17

### Added
- Idempotency: get-before-write with state comparison in 27 modules
- Pagination support (limit/offset/max_results) for all 27 info modules
- EDA event filter plugin
- Comprehensive test suites for 15 MSSQL modules
- Pre-commit and linting configuration
- Sanity tests for ansible-core 2.16/2.17/2.18/2.20

### Fixed
- Pylint unhashable-member false positives resolved
- Stale sanity ignore files removed
- Role README files added for Galaxy compliance
- Galaxy import validation issues resolved
- CI failures resolved

## [1.2.0] - 2026-05-15

### Added
- 54 modules covering full Microsoft SQL Server platform
- 10 Day-2 operation roles
- EDA source plugins
- Dynamic inventory plugin

## [1.0.0] - 2026-05-15

### Added
- Initial release with database, login, user, role, AG, TDE, and Agent job modules
- EDA event-driven automation support
- Unit tests and CI pipeline
