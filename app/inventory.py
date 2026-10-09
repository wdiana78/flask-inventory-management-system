
class Inventory:
    """Manage inventory items in an in-memory list."""

    def __init__(self):
        self.items = []
        self.next_id = 1

    def get_all(self):
        return self.items

    def get_by_id(self, item_id):
        return next(
            (item for item in self.items if item["id"] == item_id),
            None
        )

    def create(self, data):
        item = {
            "id": self.next_id,
            "name": data["name"],
            "barcode": data.get("barcode"),
            "brand": data.get("brand"),
            "quantity": data.get("quantity", 0),
            "price": data.get("price", 0.0),
        }

        self.items.append(item)
        self.next_id += 1
        return item

    def update(self, item_id, data):
        item = self.get_by_id(item_id)

        if item is None:
            return None

        allowed_fields = {
            "name", "barcode", "brand", "quantity", "price"
        }

        for field, value in data.items():
            if field in allowed_fields:
                item[field] = value

        return item

    def delete(self, item_id):
        item = self.get_by_id(item_id)

        if item is None:
            return False

        self.items.remove(item)
        return True


inventory = Inventory()
