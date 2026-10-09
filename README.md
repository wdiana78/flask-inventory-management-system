# Flask Inventory Management System

A Flask REST API for managing inventory and retrieving product information from OpenFoodFacts, with a command-line interface (CLI) for interacting with the API.

## Features

- Create, list, retrieve, update, and delete inventory items.
- Look up products using a barcode.
- Search for products by name.
- Import an external product into inventory by barcode (name, brand, barcode, and ingredients are saved).
- Health-check endpoint.
- Command-line interface for all inventory operations.
- Automated tests using pytest and unittest.mock.

## Technology Stack

- Python 3.12
- Flask
- Requests
- pytest
- OpenFoodFacts API

## Project Structure

```
app/
  __init__.py              Flask app factory
  inventory.py             In-memory inventory storage (array)
  routes/
    inventory_routes.py    API routes (CRUD + OpenFoodFacts)
  services/
    openfoodfacts.py       OpenFoodFacts API client
  cli/
    inventory_cli.py       Command-line interface
tests/                     pytest test suite
run.py                     Starts the development server
requirements.txt           Python dependencies
```

## Setup

Clone the repository:

```
git clone https://github.com/wdiana78/flask-inventory-management-system.git
cd flask-inventory-management-system
```

Create and activate a virtual environment:

```
python3 -m venv .venv
source .venv/bin/activate
```

On Windows (PowerShell), activate with `.venv\Scripts\Activate.ps1` instead.

Install dependencies:

```
python -m pip install -r requirements.txt
```

## Run the API

```
python run.py
```

The development server runs at http://127.0.0.1:5000 and starts in Flask debug mode.

## API Endpoints

| Method | Endpoint                              | Description                            |
| ------ | ------------------------------------- | -------------------------------------- |
| GET    | `/`                                   | API welcome message                    |
| GET    | `/health`                             | Health check                           |
| GET    | `/inventory`                          | List inventory items                   |
| GET    | `/inventory/<item_id>`                | Retrieve one item                      |
| POST   | `/inventory`                          | Create an item                         |
| PATCH  | `/inventory/<item_id>`                | Update an item                         |
| DELETE | `/inventory/<item_id>`                | Delete an item                         |
| GET    | `/products/barcode/<barcode>`         | Look up an external product by barcode |
| GET    | `/products/search?name=<name>`        | Search external products by name       |
| POST   | `/inventory/import/barcode/<barcode>` | Import a product into inventory        |

### Status codes

| Code | Meaning                                        |
| ---- | ---------------------------------------------- |
| 200  | Success                                        |
| 201  | Item created or imported                       |
| 204  | Item deleted                                   |
| 400  | Invalid input (for example, missing item name) |
| 404  | Item or product not found                      |
| 502  | OpenFoodFacts is unavailable                   |

## Inventory Item Fields

| Field         | Description                                             |
| ------------- | ------------------------------------------------------- |
| `id`          | Unique number assigned automatically                    |
| `name`        | Product name (required)                                 |
| `barcode`     | Product barcode                                         |
| `brand`       | Brand name                                              |
| `quantity`    | Stock level (default 0)                                 |
| `price`       | Price (default 0.0)                                     |
| `ingredients` | Ingredients text (filled in when a product is imported) |

## Create an Inventory Item

Send a POST request to `/inventory` with a JSON body:

```json
{
  "name": "Soap",
  "barcode": "12345",
  "brand": "Example Brand",
  "quantity": 5,
  "price": 100
}
```

## Import a Product

Send a POST request to:

```
/inventory/import/barcode/3017620422003
```

A successful import returns HTTP 201 and the newly created inventory item, including the product name, barcode, brand, and ingredients from OpenFoodFacts. An unknown barcode returns 404.

## Command-Line Interface (CLI)

The CLI communicates with the running Flask API. Start the API in one terminal:

```
python run.py
```

In a second terminal, activate the virtual environment and run these commands from the project root.

List all inventory items:

```
python -m app.cli.inventory_cli list
```

View one item:

```
python -m app.cli.inventory_cli show 1
```

Add an item:

```
python -m app.cli.inventory_cli add "Soap" --barcode 12345 --brand "Example Brand" --quantity 5 --price 100
```

Update an item:

```
python -m app.cli.inventory_cli update 1 --quantity 8
```

Delete an item:

```
python -m app.cli.inventory_cli delete 1
```

Search external products by name:

```
python -m app.cli.inventory_cli search "Nutella"
```

Look up an external product by barcode:

```
python -m app.cli.inventory_cli barcode 3017620422003
```

Import an external product into inventory:

```
python -m app.cli.inventory_cli import 3017620422003
```

Check API health:

```
python -m app.cli.inventory_cli health
```

Display all available commands:

```
python -m app.cli.inventory_cli --help
```

The CLI reports unsuccessful HTTP responses and connection errors with a non-zero exit status.

## Run Tests

```
python -m pytest -q
```

The tests cover the API routes, the CLI commands, and the OpenFoodFacts client. External HTTP responses are mocked, so the tests do not require a live API server or network access.

## Storage Limitation

Inventory is stored in memory and resets when the Flask process restarts. Persistent database storage is not implemented.

## External API

Product data is provided by [OpenFoodFacts](https://world.openfoodfacts.org/). External requests can fail when the service is unavailable.

## Educational Use

This project was developed as part of a software development course.
