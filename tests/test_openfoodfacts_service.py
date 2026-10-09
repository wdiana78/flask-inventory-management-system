from unittest.mock import Mock

import pytest
import requests

from app.services import openfoodfacts


def test_lookup_by_barcode_returns_product(monkeypatch):
    response = Mock()
    response.json.return_value = {
        "status": 1,
        "product": {
            "product_name": "Nutella",
            "code": "3017620422003",
            "brands": "Ferrero",
            "ingredients_text": "Sugar, palm oil, hazelnuts",
        },
    }
    response.raise_for_status.return_value = None

    request_mock = Mock(return_value=response)
    monkeypatch.setattr(requests, "get", request_mock)

    result = openfoodfacts.lookup_by_barcode("3017620422003")

    assert result == {
        "name": "Nutella",
        "barcode": "3017620422003",
        "brand": "Ferrero",
        "ingredients": "Sugar, palm oil, hazelnuts",
    }
    request_mock.assert_called_once()


def test_lookup_by_barcode_returns_none_when_not_found(monkeypatch):
    response = Mock()
    response.json.return_value = {"status": 0}
    response.raise_for_status.return_value = None
    monkeypatch.setattr(requests, "get", Mock(return_value=response))

    assert openfoodfacts.lookup_by_barcode("0000000000000") is None


def test_lookup_by_barcode_returns_none_on_http_404(monkeypatch):
    # OpenFoodFacts answers HTTP 404 for an unknown barcode.
    response = Mock()
    response.status_code = 404
    monkeypatch.setattr(requests, "get", Mock(return_value=response))

    assert openfoodfacts.lookup_by_barcode("0000000000000") is None


def test_lookup_by_name_returns_products(monkeypatch):
    response = Mock()
    response.json.return_value = {
        "products": [
            {
                "product_name": "Nutella",
                "code": "3017620422003",
                "brands": "Ferrero",
            },
            {"product_name": "", "code": "123", "brands": "Unknown"},
        ]
    }
    response.raise_for_status.return_value = None

    request_mock = Mock(return_value=response)
    monkeypatch.setattr(requests, "get", request_mock)

    result = openfoodfacts.lookup_by_name("Nutella")

    assert result == [
        {
            "name": "Nutella",
            "barcode": "3017620422003",
            "brand": "Ferrero",
        }
    ]
    assert request_mock.call_args.kwargs["params"]["search_terms"] == "Nutella"


def test_lookup_by_barcode_raises_on_http_error(monkeypatch):
    response = Mock()
    response.raise_for_status.side_effect = requests.HTTPError("Service unavailable")
    monkeypatch.setattr(requests, "get", Mock(return_value=response))

    with pytest.raises(requests.HTTPError):
        openfoodfacts.lookup_by_barcode("3017620422003")