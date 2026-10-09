"""In-memory inventory storage used by the API."""


class Inventory:
    """Manage inventory items in an in-memory list.

    Data is lost when the Flask process restarts (there is no database).
    """

    # Fields a client is allowed to change through update().
    ALLOWED_FIELDS = {
        "name", "barcode", "brand", "quantity", "price", "ingredients"
    }

    def __init__(self):
        self.items = []
        self.next_id = 1

    def get_all(self):
        """Return every inventory item."""
        return self.items

    def get_by_id(self, item_id):
        """Return the item with the given id, or None if it does not exist."""
        return next(
            (item for item in self.items if item["id"] == item_id),
            None
        )

    def create(self, data):
        """Create an item from `data`, assign it a unique id, and store it.

        Only `name` is required. Optional fields fall back to defaults.
        """
        item = {
            "id": self.next_id,
            "name": data["name"],
            "barcode": data.get("barcode"),
            "brand": data.get("brand"),
            "quantity": data.get("quantity", 0),
            "price": data.get("price", 0.0),
            "ingredients": data.get("ingredients"),
        }

        self.items.append(item)
        self.next_id += 1
        return item

    def update(self, item_id, data):
        """Update allowed fields of an item. Return the item, or None if missing."""
        item = self.get_by_id(item_id)

        if item is None:
            return None

        # Ignore unknown fields so clients cannot overwrite the id.
        for field, value in data.items():
            if field in self.ALLOWED_FIELDS:
                item[field] = value

        return item

    def delete(self, item_id):
        """Delete an item. Return True if it existed, False otherwise."""
        item = self.get_by_id(item_id)

        if item is None:
            return False

        self.items.remove(item)
        return True


inventory = Inventory()