import sys
from unittest.mock import Mock

import pytest
import requests

from app.cli import inventory_cli


def make_response(status_code=200, json_data=None):
    response = Mock()
    response.status_code = status_code
    response.ok = status_code < 400
    response.json.return_value = json_data
    return response


def test_list_command(monkeypatch):
    request_mock = Mock(return_value=make_response(200, [{"id": 1, "name": "Soap"}]))
    monkeypatch.setattr(requests, "request", request_mock)
    monkeypatch.setattr(sys, "argv", ["inventory_cli", "list"])

    result = inventory_cli.main()

    assert result == 0
    request_mock.assert_called_once_with(
        "GET", "http://127.0.0.1:5000/inventory", timeout=10
    )


def test_add_command(monkeypatch):
    request_mock = Mock(return_value=make_response(201, {"id": 1, "name": "Soap"}))
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
    request_mock = Mock(return_value=make_response(204))
    monkeypatch.setattr(requests, "request", request_mock)
    monkeypatch.setattr(sys, "argv", ["inventory_cli", "delete", "1"])

    result = inventory_cli.main()

    assert result == 0
    request_mock.assert_called_once_with(
        "DELETE", "http://127.0.0.1:5000/inventory/1", timeout=10
    )


def test_api_error_returns_nonzero(monkeypatch):
    response = make_response(404, {"error": "Item not found"})
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


def test_health_command(monkeypatch):
    request_mock = Mock(return_value=make_response(200, {"status": "healthy"}))
    monkeypatch.setattr(requests, "request", request_mock)
    monkeypatch.setattr(sys, "argv", ["inventory_cli", "health"])

    result = inventory_cli.main()

    assert result == 0
    request_mock.assert_called_once_with(
        "GET", "http://127.0.0.1:5000/health", timeout=10
    )


def test_show_command(monkeypatch):
    request_mock = Mock(return_value=make_response(200, {"id": 1, "name": "Soap"}))
    monkeypatch.setattr(requests, "request", request_mock)
    monkeypatch.setattr(sys, "argv", ["inventory_cli", "show", "1"])

    result = inventory_cli.main()

    assert result == 0
    request_mock.assert_called_once_with(
        "GET", "http://127.0.0.1:5000/inventory/1", timeout=10
    )


def test_update_command(monkeypatch):
    request_mock = Mock(return_value=make_response(200, {"id": 1, "quantity": 8}))
    monkeypatch.setattr(requests, "request", request_mock)
    monkeypatch.setattr(
        sys, "argv", ["inventory_cli", "update", "1", "--quantity", "8"]
    )

    result = inventory_cli.main()

    assert result == 0
    request_mock.assert_called_once_with(
        "PATCH",
        "http://127.0.0.1:5000/inventory/1",
        timeout=10,
        json={"quantity": 8},
    )


def test_update_without_fields_exits_with_error(monkeypatch):
    request_mock = Mock()
    monkeypatch.setattr(requests, "request", request_mock)
    monkeypatch.setattr(sys, "argv", ["inventory_cli", "update", "1"])

    with pytest.raises(SystemExit) as exc_info:
        inventory_cli.main()

    assert exc_info.value.code == 2
    request_mock.assert_not_called()


def test_search_command(monkeypatch):
    request_mock = Mock(
        return_value=make_response(200, [{"product_name": "Nutella"}])
    )
    monkeypatch.setattr(requests, "request", request_mock)
    monkeypatch.setattr(sys, "argv", ["inventory_cli", "search", "Nutella"])

    result = inventory_cli.main()

    assert result == 0
    request_mock.assert_called_once_with(
        "GET",
        "http://127.0.0.1:5000/products/search",
        timeout=10,
        params={"name": "Nutella"},
    )


def test_barcode_command(monkeypatch):
    request_mock = Mock(
        return_value=make_response(200, {"product_name": "Nutella"})
    )
    monkeypatch.setattr(requests, "request", request_mock)
    monkeypatch.setattr(
        sys, "argv", ["inventory_cli", "barcode", "3017620422003"]
    )

    result = inventory_cli.main()

    assert result == 0
    request_mock.assert_called_once_with(
        "GET",
        "http://127.0.0.1:5000/products/barcode/3017620422003",
        timeout=10,
    )


def test_import_command(monkeypatch):
    request_mock = Mock(
        return_value=make_response(201, {"id": 1, "name": "Nutella"})
    )
    monkeypatch.setattr(requests, "request", request_mock)
    monkeypatch.setattr(
        sys, "argv", ["inventory_cli", "import", "3017620422003"]
    )

    result = inventory_cli.main()

    assert result == 0
    request_mock.assert_called_once_with(
        "POST",
        "http://127.0.0.1:5000/inventory/import/barcode/3017620422003",
        timeout=10,
    )