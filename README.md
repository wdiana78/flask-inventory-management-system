# Flask Inventory Management System

A Flask REST API for managing inventory and retrieving product information from OpenFoodFacts.

## Features

- Create, list, retrieve, update, and delete inventory items.
- Look up products using a barcode.
- Search for products by name.
- Import an external product into inventory by barcode.
- Health-check endpoint.
- Automated API tests using pytest.

## Technology Stack

- Python 3.12
- Flask
- Requests
- pytest
- OpenFoodFacts API

## Setup

Clone the repository:

    git clone git@github.com:wdiana78/flask-inventory-management-system.git
    cd flask-inventory-management-system

Create and activate a virtual environment:

    python3 -m venv .venv
    source .venv/bin/activate

Install dependencies:

    python -m pip install -r requirements.txt

## Run the API

    python run.py

The development server runs at http://127.0.0.1:5000.

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| GET | `/` | API welcome message |
| GET | `/health` | Health check |
| GET | `/inventory` | List inventory items |
| GET | `/inventory/<item_id>` | Retrieve one item |
| POST | `/inventory` | Create an item |
| PATCH | `/inventory/<item_id>` | Update an item |
| DELETE | `/inventory/<item_id>` | Delete an item |
| GET | `/products/barcode/<barcode>` | Look up an external product by barcode |
| GET | `/products/search?name=<name>` | Search external products by name |
| POST | `/inventory/import/barcode/<barcode>` | Import a product into inventory |

## Create an Inventory Item

Send a POST request to `/inventory` with a JSON body:

    {
      "name": "Soap",
      "barcode": "12345",
      "brand": "Example Brand",
      "quantity": 5,
      "price": 100
    }

## Import a Product

Send a POST request to:

    /inventory/import/barcode/3017620422003

A successful import returns HTTP 201 and the newly created inventory item.

## Run Tests

    python -m pytest -q

The tests mock external API responses where appropriate, avoiding dependence on the availability of OpenFoodFacts.

## Storage Limitation

Inventory is stored in memory and resets when the Flask process restarts. Persistent database storage is not implemented.

## External API

Product data is provided by [OpenFoodFacts](https://world.openfoodfacts.org/). External requests can fail when the service is unavailable.

## Educational Use

This project was developed as part of a software development course.

## Command-Line Interface (CLI)

The CLI communicates with the running Flask API. Start the API in one terminal:

    python run.py

In a second terminal, activate the virtual environment and run these commands from the project root.

List all inventory items:

    python -m app.cli.inventory_cli list

View one item:

    python -m app.cli.inventory_cli show 1

Add an item:

    python -m app.cli.inventory_cli add "Soap" --barcode 12345 --brand "Example Brand" --quantity 5 --price 100

Update an item:

    python -m app.cli.inventory_cli update 1 --quantity 8

Delete an item:

    python -m app.cli.inventory_cli delete 1

Search external products by name:

    python -m app.cli.inventory_cli search "Nutella"

Look up an external product by barcode:

    python -m app.cli.inventory_cli barcode 3017620422003

Import an external product into inventory:

    python -m app.cli.inventory_cli import 3017620422003

Display all available commands:

    python -m app.cli.inventory_cli --help

The CLI reports unsuccessful HTTP responses and connection errors with a non-zero exit status.

## Testing the CLI

The CLI tests mock HTTP responses, so they do not require a live API server or external network access.

    python -m pytest -q
