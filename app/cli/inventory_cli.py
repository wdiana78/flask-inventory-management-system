import argparse
import json
import sys

import requests

DEFAULT_BASE_URL = "http://127.0.0.1:5000"


def api_request(method, url, **kwargs):
    try:
        response = requests.request(method, url, timeout=10, **kwargs)
    except requests.RequestException as exc:
        print(f"API connection failed: {exc}", file=sys.stderr)
        return 1

    if response.status_code == 204:
        print("Success.")
        return 0

    try:
        result = response.json()
    except ValueError:
        result = response.text

    print(json.dumps(result, indent=2) if isinstance(result, (dict, list)) else result)

    if not response.ok:
        print(f"HTTP {response.status_code}", file=sys.stderr)
        return 1

    return 0


def main():
    parser = argparse.ArgumentParser(description="Inventory Management CLI")
    parser.add_argument(
        "--base-url",
        default=DEFAULT_BASE_URL,
        help="Base URL of the running Flask API",
    )

    commands = parser.add_subparsers(dest="command", required=True)

    commands.add_parser("list", help="List inventory items")

    show = commands.add_parser("show", help="Show an inventory item")
    show.add_argument("id", type=int)

    add = commands.add_parser("add", help="Create an inventory item")
    add.add_argument("name")
    add.add_argument("--barcode")
    add.add_argument("--brand")
    add.add_argument("--quantity", type=int, default=0)
    add.add_argument("--price", type=float, default=0.0)

    update = commands.add_parser("update", help="Update an inventory item")
    update.add_argument("id", type=int)
    update.add_argument("--name")
    update.add_argument("--barcode")
    update.add_argument("--brand")
    update.add_argument("--quantity", type=int)
    update.add_argument("--price", type=float)

    delete = commands.add_parser("delete", help="Delete an inventory item")
    delete.add_argument("id", type=int)

    search = commands.add_parser("search", help="Search external products")
    search.add_argument("name")

    barcode = commands.add_parser("barcode", help="Look up a product by barcode")
    barcode.add_argument("barcode")

    import_product = commands.add_parser(
        "import", help="Import an external product by barcode"
    )
    import_product.add_argument("barcode")

    args = parser.parse_args()
    base_url = args.base_url.rstrip("/")

    if args.command == "list":
        return api_request("GET", f"{base_url}/inventory")

    if args.command == "show":
        return api_request("GET", f"{base_url}/inventory/{args.id}")

    if args.command == "add":
        data = {
            "name": args.name,
            "quantity": args.quantity,
            "price": args.price,
        }
        if args.barcode is not None:
            data["barcode"] = args.barcode
        if args.brand is not None:
            data["brand"] = args.brand
        return api_request("POST", f"{base_url}/inventory", json=data)

    if args.command == "update":
        data = {
            key: value
            for key, value in {
                "name": args.name,
                "barcode": args.barcode,
                "brand": args.brand,
                "quantity": args.quantity,
                "price": args.price,
            }.items()
            if value is not None
        }
        if not data:
            parser.error("Provide at least one field to update")
        return api_request("PATCH", f"{base_url}/inventory/{args.id}", json=data)

    if args.command == "delete":
        return api_request("DELETE", f"{base_url}/inventory/{args.id}")

    if args.command == "search":
        return api_request(
            "GET", f"{base_url}/products/search", params={"name": args.name}
        )

    if args.command == "barcode":
        return api_request(
            "GET", f"{base_url}/products/barcode/{args.barcode}"
        )

    if args.command == "import":
        return api_request(
            "POST", f"{base_url}/inventory/import/barcode/{args.barcode}"
        )

    return 0


if __name__ == "__main__":
    sys.exit(main())
