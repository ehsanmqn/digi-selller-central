import requests

from seller_products import SellerProducts


class DigikalaInventory:
    def __init__(self):
        self.api_url = 'https://sandbox.diginext.ir/api/v3/inventories'
        self.headers = {
            "accept": "application/json",
            "x-response-code": "200"
        }
        self.inventory_data = {}

    def fetch_inventory_data(self):
        """Fetch inventory data from the API."""
        response = requests.get(self.api_url, headers=self.headers)
        if response.status_code == 200:
            self.inventory_data = response.json().get('data', {})
        else:
            raise Exception(f"Failed to retrieve data, status code: {response.status_code}")

    def get_inventory_info(self):
        """Return the inventory information."""
        return self.inventory_data

    def get_products_with_warehouse_stock(self):
        """Filter and return products where warehouse_stock > 0."""
        products_with_stock = []
        items = self.inventory_data.get('items', [])

        for item in items:
            if item.get('warehouse_stock', 0) > 0:
                products_with_stock.append(item)

        return products_with_stock

    def extract_product_ids_from_stock(self):
        """Extract and return a set of product IDs from products with warehouse stock."""
        products_with_stock = self.get_products_with_warehouse_stock()
        product_ids = {item.get('product_id') for item in products_with_stock}
        return product_ids