from flask import Blueprint, jsonify, request

from app.inventory import inventory
from app.services.openfoodfacts import (
    lookup_by_barcode,
    lookup_by_name,
)

inventory_bp = Blueprint("inventory", __name__)


# -------------------- INVENTORY CRUD --------------------

@inventory_bp.route("/inventory", methods=["GET"])
def get_items():
    return jsonify(inventory.get_all()), 200


@inventory_bp.route("/inventory/<int:item_id>", methods=["GET"])
def get_item(item_id):
    item = inventory.get_by_id(item_id)

    if item is None:
        return jsonify({"error": "Item not found"}), 404

    return jsonify(item), 200


@inventory_bp.route("/inventory", methods=["POST"])
def create_item():
    data = request.get_json(silent=True)

    if not isinstance(data, dict) or not isinstance(data.get("name"), str):
        return jsonify({"error": "A valid item name is required"}), 400

    if not data["name"].strip():
        return jsonify({"error": "A valid item name is required"}), 400

    data["name"] = data["name"].strip()
    return jsonify(inventory.create(data)), 201


@inventory_bp.route("/inventory/<int:item_id>", methods=["PATCH"])
def update_item(item_id):
    data = request.get_json(silent=True)

    if not isinstance(data, dict) or not data:
        return jsonify(
            {"error": "A non-empty JSON object is required"}
        ), 400

    item = inventory.update(item_id, data)

    if item is None:
        return jsonify({"error": "Item not found"}), 404

    return jsonify(item), 200


@inventory_bp.route("/inventory/<int:item_id>", methods=["DELETE"])
def delete_item(item_id):
    if not inventory.delete(item_id):
        return jsonify({"error": "Item not found"}), 404

    return "", 204


# -------------------- OPENFOODFACTS INTEGRATION --------------------

@inventory_bp.route("/products/barcode/<barcode>", methods=["GET"])
def find_product_by_barcode(barcode):
    try:
        product = lookup_by_barcode(barcode)
    except Exception:
        return jsonify(
            {"error": "External product service unavailable"}
        ), 502

    if product is None:
        return jsonify({"error": "Product not found"}), 404

    return jsonify(product), 200


@inventory_bp.route("/products/search", methods=["GET"])
def search_products():
    name = request.args.get("name", "").strip()

    if not name:
        return jsonify({"error": "A product name is required"}), 400

    try:
        products = lookup_by_name(name)
    except Exception:
        return jsonify(
            {"error": "External product service unavailable"}
        ), 502

    return jsonify(products), 200


@inventory_bp.route(
    "/inventory/import/barcode/<barcode>", methods=["POST"]
)
def import_product_by_barcode(barcode):
    try:
        product = lookup_by_barcode(barcode)
    except Exception:
        return jsonify(
            {"error": "External product service unavailable"}
        ), 502

    if product is None or not product.get("name"):
        return jsonify({"error": "Product not found"}), 404

    item = inventory.create(product)
    return jsonify(item), 201
