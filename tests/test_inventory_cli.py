import sys
from unittest.mock import Mock

import requests

from app.cli import inventory_cli


def test_list_command(monkeypatch):
    response = Mock()
    response.status_code = 200
    response.ok = True
    response.json.return_value = [{"id": 1, "name": "Soap"}]

    request_mock = Mock(return_value=response)
    monkeypatch.setattr(requests, "request", request_mock)
    monkeypatch.setattr(sys, "argv", ["inventory_cli", "list"])

    result = inventory_cli.main()

    assert result == 0
    request_mock.assert_called_once_with(
        "GET", "http://127.0.0.1:5000/inventory", timeout=10
    )


def test_add_command(monkeypatch):
    response = Mock()
    response.status_code = 201
    response.ok = True
    response.json.return_value = {"id": 1, "name": "Soap"}

    request_mock = Mock(return_value=response)
    monkeypatch.setattr(requests, "request", request_mock)
    monkeypatch.setattr(
        sys,
        "argv",
        ["inventory_cli", "add", "Soap", "--quantity", "5", "--price", "100"],
    )

    result = inventory_cli.main()

    assert result == 0
    request_mock.assert_called_once_with(
        "POST",
        "http://127.0.0.1:5000/inventory",
        timeout=10,
        json={"name": "Soap", "quantity": 5, "price": 100.0},
    )


def test_delete_command(monkeypatch):
    response = Mock()
    response.status_code = 204
    response.ok = True

    request_mock = Mock(return_value=response)
    monkeypatch.setattr(requests, "request", request_mock)
    monkeypatch.setattr(sys, "argv", ["inventory_cli", "delete", "1"])

    result = inventory_cli.main()

    assert result == 0
    request_mock.assert_called_once_with(
        "DELETE", "http://127.0.0.1:5000/inventory/1", timeout=10
    )


def test_api_error_returns_nonzero(monkeypatch):
    response = Mock()
    response.status_code = 404
    response.ok = False
    response.json.return_value = {"error": "Item not found"}

    monkeypatch.setattr(requests, "request", Mock(return_value=response))
    monkeypatch.setattr(sys, "argv", ["inventory_cli", "show", "999"])

    result = inventory_cli.main()

    assert result == 1


def test_connection_error_returns_nonzero(monkeypatch):
    monkeypatch.setattr(
        requests,
        "request",
        Mock(side_effect=requests.ConnectionError("Connection refused")),
    )
    monkeypatch.setattr(sys, "argv", ["inventory_cli", "list"])

    result = inventory_cli.main()

    assert result == 1
