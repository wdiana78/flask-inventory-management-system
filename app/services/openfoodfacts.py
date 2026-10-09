import requests

BASE_URL = "https://world.openfoodfacts.org"
HEADERS = {
    "User-Agent": "FlaskInventoryManagement/1.0 (educational project)"
}
TIMEOUT = 15


def lookup_by_barcode(barcode):
    url = f"{BASE_URL}/api/v2/product/{barcode}.json"
    response = requests.get(url, headers=HEADERS, timeout=TIMEOUT)
    response.raise_for_status()

    result = response.json()
    if result.get("status") != 1:
        return None

    product = result.get("product", {})
    return {
        "name": product.get("product_name"),
        "barcode": product.get("code", barcode),
        "brand": product.get("brands"),
    }


def lookup_by_name(name):
    url = f"{BASE_URL}/api/v2/search"
    params = {
        "search_terms": name,
        "page_size": 10,
        "fields": "product_name,brands,code",
    }

    response = requests.get(
        url, params=params, headers=HEADERS, timeout=TIMEOUT
    )
    response.raise_for_status()
    data = response.json()

    return [
        {
            "name": product.get("product_name"),
            "barcode": product.get("code"),
            "brand": product.get("brands"),
        }
        for product in data.get("products", [])
        if product.get("product_name")
    ]
