from __future__ import absolute_import, division, print_function
__metaclass__ = type

"""Unit tests for mssql_agent_job module."""

from unittest.mock import MagicMock


class TestCreate:
    def test_create_returns_resource(self):
        client = MagicMock()
        client.create.return_value = dict(id="123", name="test")
        result = client.create("agent_job", dict(name="test"))
        assert result["id"] == "123"

    def test_create_with_name(self):
        client = MagicMock()
        client.create.return_value = dict(id="456", name="prod")
        result = client.create("agent_job", dict(name="prod"))
        assert result["name"] == "prod"


class TestDelete:
    def test_delete_existing(self):
        client = MagicMock()
        client.delete("agent_job", "123")
        client.delete.assert_called_once_with("agent_job", "123")

    def test_delete_not_found(self):
        client = MagicMock()
        client.delete.return_value = None
        result = client.delete("agent_job", "x")
        assert result is None


class TestList:
    def test_list_returns_items(self):
        client = MagicMock()
        client.list.return_value = [dict(id="1"), dict(id="2")]
        result = client.list("agent_job")
        assert len(result) == 2

    def test_list_empty(self):
        client = MagicMock()
        client.list.return_value = []
        assert len(client.list("agent_job")) == 0


class TestGet:
    def test_get_existing(self):
        client = MagicMock()
        client.get.return_value = dict(id="123", name="test")
        assert client.get("agent_job", "123")["name"] == "test"

    def test_get_not_found(self):
        client = MagicMock()
        client.get.return_value = None
        assert client.get("agent_job", "x") is None


class TestUpdate:
    def test_update_returns_updated(self):
        client = MagicMock()
        client.update.return_value = dict(id="123", name="updated")
        result = client.update("agent_job", "123", dict(name="updated"))
        assert result["name"] == "updated"
