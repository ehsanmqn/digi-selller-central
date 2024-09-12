import requests
from datetime import datetime, timedelta

from digikala_inventory import DigikalaInventory
from seller_products import SellerProducts


class DigikalaOrderHistory:
    def __init__(self):
        self.api_url = "https://sandbox.diginext.ir/api/v3/orders/history"
        self.headers = {
            "accept": "application/json",
            "x-response-code": "200"
        }

    def fetch_orders(self, page=1, size=50):
        params = {
            "page": page,
            "size": size,
            "sort": "id",
            "order": "asc",
            "order_type": "processed",
            "category_id": "123",
            "order_created_at_to": datetime.utcnow().isoformat() + 'Z',
            "order_created_at_from": (datetime.utcnow() - timedelta(days=30)).isoformat() + 'Z',
            "exit_from_warehouse_date_to": datetime.utcnow().isoformat() + 'Z',
            "exit_from_warehouse_date_from": (datetime.utcnow() - timedelta(days=30)).isoformat() + 'Z',
            "returned_to_warehouse_date_to": datetime.utcnow().isoformat() + 'Z',
            "returned_to_warehouse_date_from": (datetime.utcnow() - timedelta(days=30)).isoformat() + 'Z',
            "search_text_all": "1234",
            "b2b_active": "true"
        }

        response = requests.get(self.api_url, headers=self.headers, params=params)
        if response.status_code == 200:
            try:
                return response.json()
            except ValueError:
                print("Error: Response is not in JSON format")
                return {}
        else:
            print(f"Error fetching orders: {response.status_code}")
            return {}

    def get_orders_last_month(self):
        data = self.fetch_orders()
        if not data or not isinstance(data, dict) or 'data' not in data or 'items' not in data['data']:
            return {}

        orders = data['data']['items']
        orders_per_product = {}

        for order in orders:
            if not isinstance(order, dict):
                continue

            product_id = order.get('product_id')
            if product_id:
                orders_per_product[product_id] = orders_per_product.get(product_id, 0) + 1

        return orders_per_product

    def get_high_sales_products(self):
        orders_per_product = self.get_orders_last_month()
        if not orders_per_product:
            return {}

        total_sales = sum(orders_per_product.values())
        num_products = len(orders_per_product)
        average_sales = total_sales / num_products if num_products > 0 else 0

        high_sales_products = {
            product_id: sales
            for product_id, sales in orders_per_product.items()
            if sales > average_sales
        }

        return high_sales_products
