"""Client for the OpenFoodFacts API (external product data)."""

import requests

BASE_URL = "https://world.openfoodfacts.org"
# OpenFoodFacts asks API users to identify their application.
HEADERS = {
    "User-Agent": "FlaskInventoryManagement/1.0 (educational project)"
}
TIMEOUT = 15


def lookup_by_barcode(barcode):
    """Look up one product by barcode.

    Returns a dict with name, barcode, brand and ingredients, or None when
    the product does not exist. Raises requests exceptions for network
    failures and unexpected HTTP errors.
    """
    url = f"{BASE_URL}/api/v2/product/{barcode}.json"
    response = requests.get(url, headers=HEADERS, timeout=TIMEOUT)

    # OpenFoodFacts answers HTTP 404 for an unknown barcode, so treat it as
    # "not found" rather than as a service failure.
    if response.status_code == 404:
        return None

    response.raise_for_status()

    result = response.json()
    # status 1 means found; 0 means not found.
    if result.get("status") != 1:
        return None

    product = result.get("product", {})
    return {
        "name": product.get("product_name"),
        "barcode": product.get("code", barcode),
        "brand": product.get("brands"),
        "ingredients": product.get("ingredients_text"),
    }


def lookup_by_name(name):
    """Search products by name. Returns up to 10 matches (name, barcode, brand)."""
    url = f"{BASE_URL}/api/v2/search"
    params = {
        "search_terms": name,
        "page_size": 10,
        # Only request the fields we use to keep responses small.
        "fields": "product_name,brands,code",
    }

    response = requests.get(
        url, params=params, headers=HEADERS, timeout=TIMEOUT
    )
    response.raise_for_status()
    data = response.json()

    # Skip results that have no product name.
    return [
        {
            "name": product.get("product_name"),
            "barcode": product.get("code"),
            "brand": product.get("brands"),
        }
        for product in data.get("products", [])
        if product.get("product_name")
    ]