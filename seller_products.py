import requests


class SellerProducts:
    BASE_URL = "https://sandbox.diginext.ir/api/v3/products/seller"

    def __init__(self, page=1, size=50, sort="id", order="asc"):
        self.page = page
        self.size = size
        self.sort = sort
        self.order = order
        self.headers = {
            "accept": "application/json",
            "x-response-code": "200"
        }

    def get_products(self):
        params = {
            "page": self.page,
            "size": self.size,
            "sort": self.sort,
            "order": self.order,
            "search[moderation_status]": "approved"
        }
        response = requests.get(self.BASE_URL, headers=self.headers, params=params)
        response.raise_for_status()
        return response.json()

    def parse_products(self, response):
        products = response.get("data", {}).get("items", [])
        parsed_products = []
        for item in products:
            parsed_products.append({
                "variants_count": item.get("variants_count"),
                "site": item.get("site"),
                "title": item.get("title"),
                "status": item.get("status"),
                "product_id": item.get("product_id"),
                "fake": item.get("fake"),
                "status_data": item.get("status_data"),
                "is_owner": item.get("is_owner"),
                "main_category_title": item.get("main_category_title"),
                "active": item.get("active"),
                "title_fa": item.get("title_fa"),
                "title_en": item.get("title_en"),
                "brand_id": item.get("brand_id"),
                "brand_title_en": item.get("brand_title_en"),
                "brand_title_fa": item.get("brand_title_fa"),
                "product_url": item.get("product_url"),
                "image_src": item.get("image_src"),
                "dimension_level": item.get("dimension_level"),
                "brand_title": item.get("brand_title"),
                "moderation_status": item.get("moderation_status", {}).get("title"),
                "adverge_url": item.get("adverge_url")
            })
        return parsed_products

    def get_and_parse_products(self):
        response = self.get_products()
        return self.parse_products(response)
