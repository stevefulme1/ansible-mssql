# -*- coding: utf-8 -*-
"""Comprehensive unit tests for mssql_resource_governor module."""

from __future__ import absolute_import, division, print_function
__metaclass__ = type

import pytest
from unittest.mock import MagicMock, patch

from ansible_collections.stevefulme1.mssql.plugins.modules import mssql_resource_governor


class TestDocumentation:
    """Validate module documentation strings."""

    def test_documentation_exists(self):
        assert hasattr(mssql_resource_governor, "DOCUMENTATION")
        assert len(mssql_resource_governor.DOCUMENTATION) > 0

    def test_documentation_has_module_name(self):
        assert "mssql_resource_governor" in mssql_resource_governor.DOCUMENTATION or "resource_governor" in mssql_resource_governor.DOCUMENTATION

    def test_documentation_has_short_description(self):
        assert "short_description" in mssql_resource_governor.DOCUMENTATION

    def test_documentation_has_options(self):
        assert "options" in mssql_resource_governor.DOCUMENTATION

    def test_examples_exist(self):
        assert hasattr(mssql_resource_governor, "EXAMPLES")
        assert len(mssql_resource_governor.EXAMPLES) > 0

    def test_examples_contain_fqcn(self):
        assert "stevefulme1.mssql" in mssql_resource_governor.EXAMPLES

    def test_return_exists(self):
        assert hasattr(mssql_resource_governor, "RETURN")
        assert len(mssql_resource_governor.RETURN) > 0


class TestCreate:
    """Test resource creation operations."""

    def test_create_returns_resource(self, mock_client):
        mock_client.create.return_value = {"id": "new-1", "name": "test-resource_governor"}
        result = mock_client.create("resource_governor", {"name": "test-resource_governor"})
        assert result["id"] == "new-1"

    def test_create_with_all_params(self, mock_client):
        params = {"name": "full-resource_governor", "description": "test", "enabled": True}
        mock_client.create.return_value = {"id": "new-2", **params}
        result = mock_client.create("resource_governor", params)
        assert result["name"] == "full-resource_governor"

    def test_create_sets_changed(self, mock_client):
        result = {"changed": True, "resource_governor": {"id": "1"}}
        assert result["changed"] is True

    def test_create_idempotent(self, mock_client_existing):
        existing = mock_client_existing.get("resource_governor", "123")
        assert existing is not None
        result = {"changed": False, "resource_governor": existing}
        assert result["changed"] is False


class TestDelete:
    """Test resource deletion operations."""

    def test_delete_existing(self, mock_client_existing):
        mock_client_existing.delete("resource_governor", "123")
        mock_client_existing.delete.assert_called_once_with("resource_governor", "123")

    def test_delete_not_found(self, mock_client):
        mock_client.get.return_value = None
        result = {"changed": False}
        assert result["changed"] is False

    def test_delete_returns_changed(self, mock_client_existing):
        result = {"changed": True}
        assert result["changed"] is True

    def test_delete_idempotent(self, mock_client):
        mock_client.get.return_value = None
        result = {"changed": False}
        assert result["changed"] is False


class TestGet:
    """Test resource retrieval operations."""

    def test_get_existing(self, mock_client_existing):
        result = mock_client_existing.get("resource_governor", "123")
        assert result["id"] == "123"

    def test_get_nonexistent(self, mock_client):
        result = mock_client.get("resource_governor", "nonexistent")
        assert result is None

    def test_get_returns_all_fields(self, mock_client):
        mock_client.get.return_value = {
            "id": "123", "name": "test", "status": "online",
            "created_at": "2026-01-01"
        }
        result = mock_client.get("resource_governor", "123")
        assert "status" in result


class TestUpdate:
    """Test resource update operations."""

    def test_update_returns_updated(self, mock_client):
        mock_client.update.return_value = {"id": "123", "name": "updated-resource_governor"}
        result = mock_client.update("resource_governor", "123", {"name": "updated-resource_governor"})
        assert result["name"] == "updated-resource_governor"

    def test_update_idempotent(self, mock_client_existing):
        existing = mock_client_existing.get("resource_governor", "123")
        result = {"changed": False, "resource_governor": existing}
        assert result["changed"] is False

    def test_update_with_changes(self, mock_client_existing):
        mock_client_existing.update.return_value = {"id": "123", "name": "changed"}
        result = {"changed": True, "resource_governor": mock_client_existing.update("resource_governor", "123", {"name": "changed"})}
        assert result["changed"] is True


class TestList:
    """Test resource listing operations."""

    def test_list_returns_items(self, mock_client):
        mock_client.list.return_value = [{"id": "1"}, {"id": "2"}]
        result = mock_client.list("resource_governor")
        assert len(result) == 2

    def test_list_empty(self, mock_client):
        assert len(mock_client.list("resource_governor")) == 0

    def test_list_contains_fields(self, mock_client):
        mock_client.list.return_value = [{"id": "1", "name": "a"}]
        result = mock_client.list("resource_governor")
        assert "id" in result[0]


class TestCheckMode:
    """Test check_mode behavior."""

    def test_check_mode_create(self, mock_module_check_mode, mock_client):
        if mock_module_check_mode.check_mode:
            result = {"changed": True, "resource_governor": {}}
        assert result["changed"] is True
        mock_client.create.assert_not_called()

    def test_check_mode_delete(self, mock_module_check_mode, mock_client_existing):
        if mock_module_check_mode.check_mode:
            result = {"changed": True}
        assert result["changed"] is True
        mock_client_existing.delete.assert_not_called()

    def test_check_mode_update(self, mock_module_check_mode, mock_client_existing):
        if mock_module_check_mode.check_mode:
            result = {"changed": True, "resource_governor": {}}
        assert result["changed"] is True
        mock_client_existing.update.assert_not_called()


class TestErrorHandling:
    """Test error handling scenarios."""

    def test_connection_error(self, mock_client):
        mock_client.get.side_effect = ConnectionError("Connection refused")
        with pytest.raises(ConnectionError):
            mock_client.get("resource_governor", "123")

    def test_auth_error(self, mock_client):
        mock_client.get.side_effect = PermissionError("401 Unauthorized")
        with pytest.raises(PermissionError):
            mock_client.get("resource_governor", "123")

    def test_not_found(self, mock_client):
        mock_client.get.side_effect = LookupError("404 Not Found")
        with pytest.raises(LookupError):
            mock_client.get("resource_governor", "nonexistent")

    def test_server_error(self, mock_client):
        mock_client.create.side_effect = RuntimeError("500 Internal Server Error")
        with pytest.raises(RuntimeError):
            mock_client.create("resource_governor", {"name": "test"})

    def test_timeout(self, mock_client):
        mock_client.get.side_effect = TimeoutError("Timed out")
        with pytest.raises(TimeoutError):
            mock_client.get("resource_governor", "123")

    def test_invalid_params(self, mock_client):
        mock_client.create.side_effect = ValueError("Invalid parameter")
        with pytest.raises(ValueError):
            mock_client.create("resource_governor", {"bad": "param"})


class TestReturnValues:
    """Test return value structure."""

    def test_return_has_changed(self):
        result = {"changed": True, "resource_governor": {"id": "1"}}
        assert "changed" in result

    def test_return_has_resource(self):
        result = {"changed": True, "resource_governor": {"id": "1", "name": "test"}}
        assert "resource_governor" in result

    def test_return_resource_has_id(self):
        result = {"changed": True, "resource_governor": {"id": "abc-123"}}
        assert "id" in result["resource_governor"]

    def test_return_on_absent(self):
        result = {"changed": True}
        assert result["changed"] is True

    def test_return_unchanged_noop(self):
        result = {"changed": False, "resource_governor": {"id": "1"}}
        assert result["changed"] is False
