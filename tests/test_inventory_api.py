import pytest

from app import create_app
from app.inventory import inventory


@pytest.fixture
def client():
    inventory.items.clear()
    inventory.next_id = 1

    app = create_app()
    app.config["TESTING"] = True

    with app.test_client() as test_client:
        yield test_client

    inventory.items.clear()
    inventory.next_id = 1


def test_home_route(client):
    response = client.get("/")
    assert response.status_code == 200
    assert response.get_json()["message"] == "Inventory Management API"


def test_health_route(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.get_json()["status"] == "healthy"


def test_get_empty_inventory(client):
    response = client.get("/inventory")
    assert response.status_code == 200
    assert response.get_json() == []


def test_create_item(client):
    response = client.post(
        "/inventory",
        json={"name": "Soap", "quantity": 5, "price": 100},
    )

    assert response.status_code == 201
    assert response.get_json()["name"] == "Soap"
    assert response.get_json()["id"] == 1


def test_create_item_rejects_missing_name(client):
    response = client.post("/inventory", json={"quantity": 5})
    assert response.status_code == 400


def test_get_item_by_id(client):
    created = client.post("/inventory", json={"name": "Soap"})
    item_id = created.get_json()["id"]

    response = client.get(f"/inventory/{item_id}")

    assert response.status_code == 200
    assert response.get_json()["name"] == "Soap"


def test_get_missing_item(client):
    response = client.get("/inventory/999")
    assert response.status_code == 404


def test_update_item(client):
    created = client.post("/inventory", json={"name": "Soap"})
    item_id = created.get_json()["id"]

    response = client.patch(
        f"/inventory/{item_id}",
        json={"quantity": 10},
    )

    assert response.status_code == 200
    assert response.get_json()["quantity"] == 10


def test_delete_item(client):
    created = client.post("/inventory", json={"name": "Soap"})
    item_id = created.get_json()["id"]

    response = client.delete(f"/inventory/{item_id}")

    assert response.status_code == 204
    assert client.get("/inventory").get_json() == []


def test_delete_missing_item(client):
    response = client.delete("/inventory/999")
    assert response.status_code == 404


def test_barcode_lookup(monkeypatch, client):
    from app.routes import inventory_routes

    monkeypatch.setattr(
        inventory_routes,
        "lookup_by_barcode",
        lambda barcode: {
            "name": "Nutella",
            "barcode": barcode,
            "brand": "Ferrero",
        },
    )

    response = client.get("/products/barcode/12345")

    assert response.status_code == 200
    assert response.get_json()["name"] == "Nutella"


def test_name_search(monkeypatch, client):
    from app.routes import inventory_routes

    monkeypatch.setattr(
        inventory_routes,
        "lookup_by_name",
        lambda name: [{"name": name, "barcode": "12345", "brand": "Test"}],
    )

    response = client.get("/products/search?name=Soap")

    assert response.status_code == 200
    assert response.get_json()[0]["name"] == "Soap"


def test_name_search_requires_name(client):
    response = client.get("/products/search")
    assert response.status_code == 400


def test_import_product_adds_to_inventory(monkeypatch, client):
    from app.routes import inventory_routes

    monkeypatch.setattr(
        inventory_routes,
        "lookup_by_barcode",
        lambda barcode: {
            "name": "Nutella",
            "barcode": barcode,
            "brand": "Ferrero",
        },
    )

    response = client.post("/inventory/import/barcode/12345")

    assert response.status_code == 201
    assert response.get_json()["name"] == "Nutella"
    assert len(client.get("/inventory").get_json()) == 1


def test_import_missing_product(monkeypatch, client):
    from app.routes import inventory_routes

    monkeypatch.setattr(
        inventory_routes,
        "lookup_by_barcode",
        lambda barcode: None,
    )

    response = client.post("/inventory/import/barcode/99999")
    assert response.status_code == 404
    assert client.get("/inventory").get_json() == []


def test_import_handles_external_service_failure(monkeypatch, client):
    from app.routes import inventory_routes

    def unavailable(barcode):
        raise RuntimeError("External service unavailable")

    monkeypatch.setattr(
        inventory_routes, "lookup_by_barcode", unavailable
    )

    response = client.post("/inventory/import/barcode/12345")

    assert response.status_code == 502
    assert client.get("/inventory").get_json() == []
