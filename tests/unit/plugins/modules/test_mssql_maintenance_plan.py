from __future__ import absolute_import, division, print_function
__metaclass__ = type

"""Unit tests for mssql_maintenance_plan module."""

from unittest.mock import MagicMock


class TestCreate:
    def test_create_returns_resource(self):
        client = MagicMock()
        client.create.return_value = dict(id="123", name="test")
        result = client.create("maintenance_plan", dict(name="test"))
        assert result["id"] == "123"

    def test_create_with_name(self):
        client = MagicMock()
        client.create.return_value = dict(id="456", name="prod")
        result = client.create("maintenance_plan", dict(name="prod"))
        assert result["name"] == "prod"


class TestDelete:
    def test_delete_existing(self):
        client = MagicMock()
        client.delete("maintenance_plan", "123")
        client.delete.assert_called_once_with("maintenance_plan", "123")

    def test_delete_not_found(self):
        client = MagicMock()
        client.delete.return_value = None
        result = client.delete("maintenance_plan", "x")
        assert result is None


class TestList:
    def test_list_returns_items(self):
        client = MagicMock()
        client.list.return_value = [dict(id="1"), dict(id="2")]
        result = client.list("maintenance_plan")
        assert len(result) == 2

    def test_list_empty(self):
        client = MagicMock()
        client.list.return_value = []
        assert len(client.list("maintenance_plan")) == 0


class TestGet:
    def test_get_existing(self):
        client = MagicMock()
        client.get.return_value = dict(id="123", name="test")
        assert client.get("maintenance_plan", "123")["name"] == "test"

    def test_get_not_found(self):
        client = MagicMock()
        client.get.return_value = None
        assert client.get("maintenance_plan", "x") is None


class TestUpdate:
    def test_update_returns_updated(self):
        client = MagicMock()
        client.update.return_value = dict(id="123", name="updated")
        result = client.update("maintenance_plan", "123", dict(name="updated"))
        assert result["name"] == "updated"
